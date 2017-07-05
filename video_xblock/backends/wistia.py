# -*- coding: utf-8 -*-
"""
Wistia Video player plugin.
"""

import HTMLParser
import json
import httplib
import re

import requests
import babelfish

from video_xblock import BaseVideoPlayer
from video_xblock.constants import TranscriptSource
from video_xblock.utils import ugettext as _
from video_xblock.exceptions import VideoXBlockException


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
        'download_url': 'api.wistia.com/v1/medias/{media_id}/captions.json?api_password={token}',
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
        fields_list = super(WistiaPlayer, self).advanced_fields
        # Add `token` field before `threeplaymedia_file_id`
        fields_list.insert(fields_list.index('threeplaymedia_file_id'), 'token')
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
                    'url': 'default_url_to_be_replaced'
                },
                # ...
            ]
        """
        video_id = kwargs.get('video_id')
        token = kwargs.get('token')
        url = self.captions_api['url'].format(token=token, media_id=video_id)
        message = ''
        self.default_transcripts = []
        # Fetch available transcripts' languages (codes and English labels), and assign its' urls.
        try:
            data = requests.get('https://' + url)
        except requests.exceptions.RequestException as exception:
            # Probably, current API has changed
            message = 'No timed transcript may be fetched from a video platform. ' \
                      'Error: {}'.format(str(exception))
            return self.default_transcripts, message

        if data.status_code == httplib.OK:
            try:
                wistia_data = json.loads(data.text)
            except ValueError:
                wistia_data = False

            if wistia_data:
                transcripts_data = [
                    [el.get('language'), el.get('english_name'), el.get('text')]
                    for el in wistia_data
                ]
                # Populate default_transcripts
                for lang_code, lang_label, text in transcripts_data:
                    # lang_code, fetched from Wistia API, is a 3 character language code as specified by ISO-639-2.
                    # Reference: https://wistia.com/doc/data-api#captions_show
                    # Convert from ISO-639-2 to ISO-639-1; reference: https://pythonhosted.org/babelfish/
                    try:
                        lang_code = babelfish.Language(lang_code).alpha2
                    except ValueError:
                        # In case of B or T codes, e.g. 'fre'.
                        # Reference: https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
                        lang_code = babelfish.Language.fromalpha3b(lang_code).alpha2   # pylint: disable=no-member
                    lang_label = self.get_transcript_language_parameters(lang_code)[1]
                    # We already have transcript’s text by now. Don't need another one call to API
                    # The structure of default_transcripts requires to have `url`. Added it with an empty value
                    self.default_transcripts.append({
                        'lang': lang_code,
                        'label': lang_label,
                        'url': '',
                        'text': text,
                        'source': TranscriptSource.DEFAULT,
                    })
            # If captions do not exist for a video, the response will be an empty JSON array.
            # Reference: https://wistia.com/doc/data-api#captions_index
            else:
                message = 'For now, video platform doesn\'t have any timed transcript for this video.'
        # If a video does not exist, the response will be an empty HTTP 404 Not Found.
        # Reference: https://wistia.com/doc/data-api#captions_index
        elif data.status_code == httplib.NOT_FOUND:
            message = "Wistia video {video_id} doesn't exist.".format(video_id=str(video_id))
        else:
            message = "Invalid request."
        return self.default_transcripts, message

    @staticmethod
    def format_transcript_text_line(line):
        """
        Replace comma with dot in timings, e.g. 00:00:10,500 should be 00:00:10.500.
        """
        new_line = u""
        for token in line.split():
            decoded_token = token.encode('utf8', 'ignore')
            formatted_token = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', decoded_token)
            new_line += unicode(formatted_token.decode('utf8')) + u" "
        return new_line

    def format_transcript_text(self, text):
        """
        Prepare unicode transcripts to be converted to WebVTT format.
        """
        new_text = [
            self.format_transcript_text_line(line)
            for line in text[0].splitlines()
        ]
        new_text = '\n'.join(new_text)
        html_parser = HTMLParser.HTMLParser()
        unescaped_text = html_parser.unescape(new_text)
        if u"WEBVTT" not in text:
            text = u"WEBVTT\n\n" + unicode(unescaped_text)
        else:
            text = unicode(unescaped_text)
        return text

    def download_default_transcript(self, url=None, language_code=None):  # pylint: disable=unused-argument
        """
        Get default transcript fetched from a video platform API and formats it to WebVTT-like unicode.

        Though Wistia provides a method for a transcript fetching, this is to avoid API call.
        References:
            https://wistia.com/doc/data-api#captions_index
            https://wistia.com/doc/data-api#captions_show

        Arguments:
            url (str): API url to fetch a default transcript from.
            language_code (str): Language code of a default transcript to be downloaded.
        Returns:
            text (unicode): Text of transcripts.
        """
        if language_code is None:
            raise VideoXBlockException(_('`language_code` parameter is required.'))
        text = [
            sub.get(u'text')
            for sub in self.default_transcripts
            if sub.get(u'lang') == unicode(language_code)
        ]
        text = self.format_transcript_text(text) if text else u""
        return text

    def dispatch(self, request, suffix):
        """
        Wistia dispatch method.
        """
        pass
