# -*- coding: utf-8 -*-
"""
Vimeo Video player plugin.
"""

import httplib
import json
import logging
import re

import requests

from video_xblock import BaseVideoPlayer, ApiClientError
from video_xblock.backends.base import BaseApiClient
from video_xblock.utils import ugettext as _, remove_escaping

log = logging.getLogger(__name__)


class VimeoApiClientError(ApiClientError):
    """
    Vimeo specific api client errors.
    """

    default_msg = _('Vimeo API error.')


class VimeoApiClient(BaseApiClient):
    """
    Low level Vimeo API client.

    Does all heavy lifting of sending https requests over the wire.
    Responsible for API credentials issuing and access_token refreshing.
    """

    def __init__(self, token=None):
        """
        Initialize Vimeo API client.
        """
        self.access_token = token or ''

    def get(self, url, headers=None, can_retry=False):
        """
        Issue REST GET request to a given URL. Can throw ApiClientError or its subclass.

        Arguments:
            url (str): API url to fetch a resource from.
            headers (dict): Headers necessary as per API, e.g. authorization bearer to perform
            authorised requests.
        Returns:
            Response in python native data format.
        """
        headers_ = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Accept': 'application/json'
        }
        if headers is not None:
            headers_.update(headers)
        resp = requests.get(url, headers=headers_)
        if resp.status_code == httplib.OK:
            return resp.json()
        else:
            raise VimeoApiClientError(_("Can't fetch requested data from API."))

    def post(self, url, payload, headers=None, can_retry=False):
        """
        Issue REST POST request to a given URL. Can throw ApiClientError or its subclass.
        """
        raise VimeoApiClientError(_('Advanced API operations not allowed for now.'))


class VimeoPlayer(BaseVideoPlayer):
    """
    VimeoPlayer is used for videos hosted on vimeo.com.
    """

    # Regex is taken from http://regexr.com/3a2p0
    # Reference: https://vimeo.com/153979733
    url_re = re.compile(r'https?:\/\/(.+)?(vimeo.com)\/(?P<media_id>.*)')

    metadata_fields = ['access_token']
    default_transcripts_in_vtt = True

    # Current Vimeo api for requesting transcripts.

    # Note: Vimeo will automatically delete tokens that have not been used for an extended period of time.
    #       If your API calls are months apart you might need to create a new token.

    # For example: GET https://api.vimeo.com/videos/204151304/texttracks
    # Docs on captions: https://developer.vimeo.com/api/endpoints/videos#/%7Bvideo_id%7D/texttracks
    # Docs on auth: https://developer.vimeo.com/api/authentication
    captions_api = {
        'url': 'https://api.vimeo.com/videos/{media_id}/texttracks',
        'authorised_request_header': {
            'Authorization': 'Bearer {access_token}'
        },
        'response': {
            'total': '{transcripts_count}',
            'data': [
                {
                    'uri': '/texttracks/{transcript_id}',
                    'active': 'true',
                    'type': 'subtitles',
                    'language': 'en',  # no language_label translated in English may be fetched from API
                    'link': 'https://{link_to_vtt_file}',
                    'link_expires_time': 1497954324,
                    'hls_link': 'https://{link_to_vtt_file_with_hls}',
                    'hls_link_expires_time': 1497954324,
                    'name': '{captions_file_name.vtt}'
                }
            ]
        }
    }

    def __init__(self, xblock):
        """
        Initialize Vimeo player class object.
        """
        super(VimeoPlayer, self).__init__(xblock)
        self.api_client = VimeoApiClient(token=xblock.token)

    @property
    def advanced_fields(self):
        """
        Tuple of VideoXBlock fields to display in Advanced tab of edit modal window.

        Vimeo videos require Access token to be set.
        """
        return super(VimeoPlayer, self).advanced_fields

    @property
    def trans_fields(self):
        """
        List of VideoXBlock fields to display on `Manual & default transcripts` panel.
        """
        fields_list = super(VimeoPlayer, self).trans_fields
        # Add `token` after `default_transcripts`
        fields_list.append('token')
        return fields_list

    fields_help = {
        'href': _('URL of the video page. E.g. https://vimeo.com/987654321'),
        'token': _(
            'You can generate a Vimeo access token via <b>Application console\'s Authentication section</b> by '
            '<a href="https://developer.vimeo.com/apps/new" '
            'target="_blank">creating new app</a>. Please ensure appropriate operations '
            'scope ("private") has been set for access token.'
        )
    }

    def media_id(self, href):
        """
        Extract Platform's media id from the video url.

        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['data_setup'] = json.dumps(VimeoPlayer.player_data_setup(context))

        frag = super(VimeoPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/vimeo.html', **context)
        )
        js_files = [
            'static/vendor/js/Vimeo.js',
            'static/vendor/js/videojs-offset.min.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @staticmethod
    def player_data_setup(context):
        """
        Vimeo Player data setup.
        """
        result = BaseVideoPlayer.player_data_setup(context)
        del result["playbackRates"]
        del result["plugins"]["videoJSSpeedHandler"]
        result.update({
            "techOrder": ["vimeo"],
            "sources": [{
                "type": "video/vimeo",
                "src": context['url']
            }],
            "vimeo": {"iv_load_policy": 1},
        })
        return result

    def get_default_transcripts(self, **kwargs):
        """
        Fetch transcripts list from a video platform.

        Arguments:
            kwargs (dict): Key-value pairs with video_id, fetched from video xblock,
                           and access_token for Vimeo API.
        Returns:
            default_transcripts (list): list of dicts of transcripts. Example:
                [
                    {
                        'lang': 'en',
                        'label': 'English',
                        'url': 'captions.cloud.vimeo.com/captions/{transcript_id}.vtt?expires=1497970668&sig=
                                {signature_hash}&download={file_name.vtt}"'
                    },
                    # ...
                ]
            message (str): Message for a user with details on default transcripts fetching outcomes.
        """
        if not self.api_client.access_token:
            raise VimeoApiClientError(_('No API credentials provided.'))

        video_id = kwargs.get('video_id')
        url = self.captions_api['url'].format(media_id=video_id)
        message = _('Default transcripts successfully fetched from a video platform.')
        default_transcripts = []
        # Fetch available transcripts' languages and urls.
        try:
            json_data = self.api_client.get(url)
        except VimeoApiClientError:
            message = _('No timed transcript may be fetched from a video platform.<br>')
            return default_transcripts, message

        if not json_data:
            message = _('There are no default transcripts for the video on the video platform.')
            return default_transcripts, message

        # Populate default_transcripts
        transcripts_data = json_data.get('data')
        try:
            default_transcripts = self.parse_vimeo_texttracks(transcripts_data)
            return default_transcripts, message
        except VimeoApiClientError as client_exc:
            message = client_exc.detail
            return default_transcripts, message

    def parse_vimeo_texttracks(self, transcripts_data):
        """
        Pull from texttracks' Vimeo API response json_data language and url information.

        Arguments:
            transcripts_data (list of dicts): Transcripts data.
        Returns:
            transcript (dict): {language code, language label, download url}
        """
        default_transcripts = []
        for t_data in transcripts_data:
            try:
                lang_code = t_data["language"]
                lang_label = self.get_transcript_language_parameters(lang_code)[1]
                default_transcripts.append({
                    'lang': lang_code,
                    'label': lang_label,
                    'url': t_data["link"],
                })
            except KeyError:
                raise VimeoApiClientError(_('Transcripts API has been changed.'))
        log.debug("Parsed Vimeo transcripts: " + str(default_transcripts))
        return default_transcripts

    def download_default_transcript(self, url, language_code=None):  # pylint: disable=unused-argument
        """
        Download default transcript from Vimeo video platform API in WebVVT format.

        Arguments:
            url (str): Transcript download url.
        Returns:
            sub (str): Transcripts formatted per WebVTT format https://w3c.github.io/webvtt/
        """
        data = requests.get(url)
        text = data.content
        cleaned_captions_text = remove_escaping(text)
        return cleaned_captions_text
