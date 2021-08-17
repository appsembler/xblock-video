# -*- coding: utf-8 -*-
"""
Wistia Video player plugin.
"""

from html import parser as html_parser
import json
import http.client as httplib
import logging
import re

import requests
import babelfish

from video_xblock import BaseVideoPlayer
from video_xblock.constants import TranscriptSource
from video_xblock.utils import ugettext as _

log = logging.getLogger(__name__)


class WistiaPlayer(BaseVideoPlayer):
    """
    WistiaPlayer is used for videos hosted on the Wistia Video Cloud.
    """

    # From official Wistia documentation. May change in the future
    # https://wistia.com/doc/construct-an-embed-code#the_regex
    url_re = re.compile(
        r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/(?P<media_id>.*)'
    )

    # Token field is stored in metadata only if authentication was successful
    metadata_fields = ['token', ]

    # Current api (v1) for requesting transcripts.
    # For example: https://api.wistia.com/v1/medias/jzmku8z83i/captions.json
    # Docs on captions: https://wistia.com/doc/data-api#captions
    # Docs on auth: https://wistia.com/doc/data-api#authentication, https://wistia.com/doc/oauth2
    captions_api = {
        # To check on authentication status; reference: https://wistia.com/doc/data-api#authentication
        'auth_sample_url': 'api.wistia.com/v1/medias.json?api_password={token}',
        # To fetch a specific transcript; reference: https://wistia.com/doc/data-api#captions_show
        'download_url': 'http://api.wistia.com/v1/medias/{media_id}/captions/'
                        '{lang_code}.json?api_password={token}',
        # To get list of captions; reference: https://wistia.com/doc/data-api#captions_index
        'url': 'api.wistia.com/v1/medias/{media_id}/captions.json?api_password={token}',
        'response': {
            'language_code': 'language',
            'language_label': 'english_name',
            'subs': 'text'
        }
    }

    # Stores default transcripts fetched from the captions API
    default_transcripts = []

    fields_help = {
        'token': 'You can get a master token following the guide of '
                 '<a href="https://wistia.com/doc/data-api" target="_blank">Wistia</a>. '
                 'Please ensure appropriate operations scope has been set on the video platform.'
    }

    @property
    def advanced_fields(self):
        """
        Tuple of VideoXBlock fields to display in Basic tab of edit modal window.

        Brightcove videos require Brightcove Account id.
        """
        return super(WistiaPlayer, self).advanced_fields

    @property
    def trans_fields(self):
        """
        List of VideoXBlock fields to display on `Manual & default transcripts` panel.
        """
        fields_list = super(WistiaPlayer, self).trans_fields
        # Add `token` after `default_transcripts`
        fields_list.append('token')
        return fields_list

    def media_id(self, href):
        """
        Extract Platform's media id from the video url.

        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        """
        Compose an XBlock fragment with video player to be rendered in student view.

        Extend general player fragment with Wistia specific context and JavaScript.
        """
        context['data_setup'] = json.dumps(WistiaPlayer.player_data_setup(context))

        frag = super(WistiaPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/wistiavideo.html', **context)
        )

        js_files = [
            'static/vendor/js/vjs.wistia.js',
            'static/vendor/js/videojs-offset.min.js',
            'static/js/videojs/player-context-menu.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @staticmethod
    def player_data_setup(context):
        """
        Wistia Player data setup.
        """
        result = BaseVideoPlayer.player_data_setup(context)
        result.update({
            "techOrder": ["wistia"],
            "sources": [{
                "type": "video/wistia",
                "src": context['url'] + "?controlsVisibleOnLoad=false"
            }],
        })
        return result

    def authenticate_api(self, **kwargs):
        """
        Call a sample Wistia API url to check on authentication success.

        Reference:
            https://wistia.com/doc/data-api#authentication

        Arguments:
            kwargs (dict): Wistia master token key-value pair.

        Returns:
            auth_data (dict): Master token, provided by a user, which is to be stored in Wistia's player metadata.
            error_status_message (str): Message with authentication outcomes for the sake of verbosity.
        """
        token, media_id = kwargs.get('token'), kwargs.get('video_id')  # pylint: disable=unused-variable
        auth_data, error_message = {}, ''
        auth_data['token'] = token
        url = self.captions_api.get('auth_sample_url').format(token=str(token))
        response = requests.get('https://' + url)
        if response.status_code == httplib.UNAUTHORIZED:
            error_message = "Authentication failed. " \
                            "Please ensure you have provided a valid master token, using Video API Token field."
        return auth_data, error_message

    def get_default_transcripts(self, **kwargs):
        """
        Fetch transcripts list from Wistia API.

        Urls of transcripts are to be fetched later on with separate API calls.
        References:
            https://wistia.com/doc/data-api#captions_index
            https://wistia.com/doc/data-api#captions_show

        Arguments:
            kwargs (dict): Key-value pairs with video_id, fetched from video xblock, and token, fetched from Wistia API.
        Returns:
            list: List of dicts of transcripts. Example:
            [
                {
                    'lang': 'en',
                    'label': 'English',
                    'url': 'default_url_to_be_replaced',
                    'source': 'default'
                },
                # ...
            ]
        """
        video_id = kwargs.get('video_id')
        token = kwargs.get('token')
        url = self.captions_api['url'].format(token=token, media_id=video_id)

        message = _('Success.')
        self.default_transcripts = []
        # Fetch available transcripts' languages (codes and English labels), and assign its' urls.
        try:
            # get all languages caps data:
            response = requests.get('https://{}'.format(url))
        except requests.exceptions.RequestException as exc:
            # Probably, current API has changed
            message = _('No timed transcript may be fetched from a video platform.\nError details: {}').format(
                str(exc)
            )
            log.exception("Transcripts INDEX request failure.")
            return self.default_transcripts, message

        # If a video does not exist, the response will be an empty HTTP 404 Not Found.
        # Reference: https://wistia.com/doc/data-api#captions_index
        if response.status_code == httplib.NOT_FOUND:
            message = _("Wistia video {} doesn't exist.").format(video_id)
            return self.default_transcripts, message

        # Fetch other failure cases:
        if not response.ok:
            message = _("Invalid request.")
            return self.default_transcripts, message

        try:
            wistia_data = response.json()
        except ValueError:
            wistia_data = ''

        # No transcripts case, see: wistia.com/doc/data-api#captions_index
        if not wistia_data:
            message = _("For now, video platform doesn't have any timed transcript for this video.")
            return self.default_transcripts, message

        transcripts_data = [
            [el.get('language'), el.get('english_name')]
            for el in wistia_data
        ]
        # Populate default_transcripts
        for lang_code, lang_label in transcripts_data:
            download_url = self.captions_api['download_url'].format(
                media_id=video_id,
                lang_code=lang_code,
                token=token
            )
            # Wistia's API uses ISO-639-2, so "lang_code" is a 3-character code, e.g. "eng".
            # Reference: https://wistia.com/doc/data-api#captions_show
            # Convert from ISO-639-2 to ISO-639-1; reference: https://pythonhosted.org/babelfish/
            try:
                lang_code = babelfish.Language(lang_code).alpha2
            except ValueError:
                # In case of B or T codes, e.g. 'fre'.
                # Reference: https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
                lang_code = babelfish.Language.fromalpha3b(lang_code).alpha2  # pylint: disable=no-member

            lang_label = self.get_transcript_language_parameters(lang_code)[1]

            self.default_transcripts.append({
                'lang': lang_code,
                'label': lang_label,
                'url': download_url,
                'source': TranscriptSource.DEFAULT,
            })

        return self.default_transcripts, message

    @staticmethod
    def format_transcript_text_line(line):
        """
        Replace comma with dot in timings, e.g. 00:00:10,500 should be 00:00:10.500.
        """
        new_line = ""
        for token in line.split():
            decoded_token = token.encode('utf8', 'ignore')
            formatted_token = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', decoded_token)
            new_line += formatted_token.decode('utf8') + " "
        return new_line

    def format_transcript_text(self, text):
        """
        Prepare unescaped transcripts to be converted to WebVTT format.
        """
        new_text = [
            self.format_transcript_text_line(line)
            for line in text[0].splitlines()
        ]
        new_text = '\n'.join(new_text)
        unescaped_text = html_parser.unescape(new_text)
        if "WEBVTT" not in text:
            text = "WEBVTT\n\n" + unescaped_text
        else:
            text = unescaped_text
        return text

    def download_default_transcript(self, url, language_code):
        """
        Get default transcript fetched from a video platform API and format it to WebVTT-like unicode.

        References:
            https://wistia.com/doc/data-api#captions_index
            https://wistia.com/doc/data-api#captions_show

        Arguments:
            url (str): API url to fetch a default transcript from.
            language_code (str): Language ISO-639-2 code of a default transcript to be downloaded.
        Returns:
            text (str): Text of transcripts.
        """
        try:
            response = requests.get(url)
            json_data = response.json()
            return json_data['text']
        except IOError:
            log.exception("Transcript fetching failure: language [{}]".format(language_code))
            return ''
        except (ValueError, KeyError, TypeError, AttributeError):
            log.exception("Can't parse fetched transcript: language [{}]".format(language_code))
            return ''

    def dispatch(self, request, suffix):
        """
        Wistia dispatch method.
        """
        pass
