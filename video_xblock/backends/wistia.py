"""
Wistia Video player plugin
"""

import json
import re
import requests
import babelfish

from video_xblock import BaseVideoPlayer


class WistiaPlayer(BaseVideoPlayer):
    """
    WistiaPlayer is used for videos hosted on the Wistia Video Cloud
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

    def media_id(self, href):
        """
        Wistia specific implementation of BaseVideoPlayer.media_id()
        """
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        """
        Compose an XBlock fragment with video player to be rendered in student view.

        Extend general player fragment with Wistia specific context and JavaScript.
        """
        context['data_setup'] = json.dumps({
            "controlBar": {
                "volumeMenuButton": {
                    "inline": False,
                    "vertical": True
                }
            },
            "techOrder": ["wistia"],
            "sources": [{
                "type": "video/wistia",
                "src": context['url'] + "?controlsVisibleOnLoad=false"
            }],
            "playbackRates": [0.5, 1, 1.5, 2],
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time'],
                    "current_time": context['player_state']['current_time'],
                },
                "videoJSSpeedHandler": {},
            }
        })

        frag = super(WistiaPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('../static/html/wistiavideo.html', **context)
        )
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-wistia/src/wistia.js'
        ))

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-offset/dist/videojs-offset.min.js'
        ))

        frag.add_javascript(self.render_resource('../static/js/player-context-menu.js', **context))

        return frag

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        """
        Customises display of studio editor fields per a video platform.
        """
        message = 'You can get a master token following the guide of ' \
                  '<a href="https://wistia.com/doc/data-api" target="_blank">Wistia</a>. ' \
                  'Please ensure appropriate operations scope has been set on the video platform.'
        editable_fields = list(editable_fields)
        editable_fields.remove('account_id')
        editable_fields.remove('player_id')
        customised_editable_fields = tuple(editable_fields)
        return message, customised_editable_fields

    def authenticate_api(self, **kwargs):
        """
        Calls a sample Wistia API url to check on authentication success.
        Reference: https://wistia.com/doc/data-api#authentication

        Arguments:
            kwargs (dict): Wistia master token key-value pair.
        Returns:
            auth_data (dict): master token, provided by a user, is to be stored in Wistia's player metadata,
                since no access token should be generated
            error_status_message (str) for the sake of verbosity.
        """
        token, media_id = kwargs.get('token'), kwargs.get('video_id')  # pylint: disable=unused-variable
        auth_data, error_message = {}, ''
        auth_data['token'] = token
        url = self.captions_api.get('auth_sample_url').format(token=str(token))
        response = requests.get('https://' + url)
        if response.status_code == 401:
            error_message = "Authentication failed. " \
                            "Please ensure you have provided a valid master token, using Video API Token field."
        return auth_data, error_message

    def get_default_transcripts(self, **kwargs):
        """
        Fetches transcripts list from Wistia API.
        Reference: https://wistia.com/doc/data-api#captions_index

        Urls of transcipts are to be fetched later on with separate API calls.
        Reference: https://wistia.com/doc/data-api#captions_show

        Arguments:
            kwargs (dict): key-value pairs with video_id (fetched from href field of studio editor),
                           and token (fetched from Wistia API).
        Returns:
            list: List of dicts of transcripts.  Example:
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
        default_transcripts = []
        message = ''

        # Fetch available transcripts' languages (codes and English labels), and assign its' urls.
        try:
            data = requests.get('https://' + url)
            wistia_data = json.loads(data.text)
        except requests.exceptions.RequestException as exception:
            # Probably, current API has changed
            message = 'No timed transcript may be fetched from a video platform. ' \
                      'Error: {}'.format(str(exception))
            return default_transcripts, message

        if data.status_code == 200 and wistia_data:
            transcripts_data = [
                [el.get('language'), el.get('english_name')]
                for el in wistia_data]
            # Populate default_transcripts
            for lang_code, lang_label in transcripts_data:
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
                transcript_url = 'default_url_to_be_replaced'
                default_transcript = {
                    'lang': lang_code,
                    'label': lang_label,
                    'url': transcript_url,
                }
                default_transcripts.append(default_transcript)
        # If captions do not exist for a video, the response will be an empty JSON array.
        # Reference: https://wistia.com/doc/data-api#captions_index
        elif data.status_code == 200 and not wistia_data:
            message = 'For now, video platform doesn\'t have any timed transcript for this video.'
        # If a video does not exist, the response will be an empty HTTP 404 Not Found.
        # Reference: https://wistia.com/doc/data-api#captions_index
        elif data.status_code == 404:
            message = "Wistia video {video_id} doesn't exist.".format(video_id=str(video_id))

        return default_transcripts, message

    def download_default_transcript(self, url):  # pylint: disable=unused-argument
        # TODO: implement
        """
        Downloads default transcript from a video platform API in WebVVT format.

        Arguments:
            url (str): transcript download url.
        Returns:
            unicode: Transcripts in WebVTT format.
        """
        return u''
