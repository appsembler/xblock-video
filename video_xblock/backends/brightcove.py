"""
Brightcove Video player plugin
"""

import re
import base64
import json
import requests

from xblock.fragment import Fragment

from video_xblock import BaseVideoPlayer


class BrightcovePlayer(BaseVideoPlayer):
    """
    BrightcovePlayer is used for videos hosted on the Brightcove Video Cloud.
    """

    url_re = re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(?P<media_id>\d+)')
    metadata_fields = ['access_token', 'client_id', 'client_secret', ]

    # Current api for requesting transcripts.
    # For example: https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/{video_ID}
    # Docs on captions: https://docs.brightcove.com/en/video-cloud/cms-api/guides/webvtt.html
    # Docs on auth: https://docs.brightcove.com/en/video-cloud/oauth-api/getting-started/oauth-api-overview.html
    captions_api = {
        'url': 'cms.api.brightcove.com/v1/accounts/{account_id}/videos/{media_id}',
        'authorised_request_header': {
            'Authorization': 'Bearer {access_token}'
        },
        'response': {
            'language_code': 'srclang',  # no language_label translated in English may be fetched from API
            'subs': 'src'  # e.g. "http://learning-services-media.brightcove.com/captions/bc_smart_ja.vtt"
        }
    }

    def media_id(self, href):
        """
        Brightcove specific implementation of BaseVideoPlayer.media_id()
        """
        return self.url_re.match(href).group('media_id')

    def get_frag(self, **context):
        """
        Compose an XBlock fragment with video player to be rendered in student view.

        Brightcove backend is a special case and doesn't use vanila Video.js player.
        Because of this it doesn't use `super.get_frag()`
        """

        frag = Fragment(
            self.render_resource('../static/html/brightcove.html', **context)
        )
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        frag.add_content(
            self.add_js_content('../static/js/player_state.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/toggle-button.js')
        )
        if context['player_state']['transcripts']:
            frag.add_content(
                self.add_js_content('../static/bower_components/videojs-transcript/dist/videojs-transcript.js')
            )
            frag.add_content(
                self.add_js_content('../static/js/videojs-transcript.js', **context)
            )
        frag.add_content(
            self.add_js_content('../static/js/videojs-tabindex.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs_event_plugin.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/bower_components/videojs-offset/dist/videojs-offset.js')
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs-speed-handler.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/brightcove-videojs-init.js', **context)
        )
        frag.add_css(
            self.resource_string('../static/css/brightcove.css')
        )
        return frag

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        """
        Customises display of studio editor fields per a video platform.
        """
        message = 'You can generate a BC token following the guide of ' \
                  '<a href="https://docs.brightcove.com/en/video-cloud/oauth-api/guides/get-client-credentials.html" ' \
                  'target="_blank">Brightcove</a>. Please ensure appropriate operations scope has been set ' \
                  'on the video platform, and a BC token is valid.'
        return message, editable_fields

    @staticmethod
    def get_client_credentials(token, account_id):
        """
        Gets client credentials, given a client token and an account_id.
        Reference: https://docs.brightcove.com/en/video-cloud/oauth-api/guides/get-client-credentials.html
        """
        headers = {'Authorization': 'BC_TOKEN {}'.format(token)}
        data = [{
            "identity": {
                "type": "video-cloud-account",
                "account-id": int(account_id)
            },
            "operations": [
                "video-cloud/video/update"
            ]
        }]
        payload = {'maximum_scope': json.dumps(data)}
        url = 'https://oauth.brightcove.com/v4/client_credentials'
        response = requests.post(url, data=payload, headers=headers)
        response_data = json.loads(response.text)
        # New resource must have been created.
        if response.status_code == 201 and response_data:
            client_secret = response_data.get('client_secret')
            client_id = response_data.get('client_id')
            error_message = ''
        else:
            client_secret, client_id = '', ''
            # For dev purposes, response_data.get('error_description') may also be considered.
            error_message = "Authentication to Brightcove API failed: no client credentials have been retrieved.\n" \
                            "Please ensure you have provided a valid BC token, using Video API Token field."
        return client_secret, client_id, error_message

    @staticmethod
    def get_access_token(client_id, client_secret):
        """
        Gets access token from a Brightcove API to perform authorized requests.
        Reference: https://docs.brightcove.com/en/video-cloud/oauth-api/guides/get-token.html

        """
        # Authorization header: the entire {client_id}:{client_secret} string must be Base64-encoded
        client_credentials_encoded = base64.b64encode('{client_id}:{client_secret}'.format(
            client_id=client_id,
            client_secret=client_secret))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(client_credentials_encoded)
        }
        data = {'grant_type': 'client_credentials'}
        url = 'https://oauth.brightcove.com/v3/access_token'
        response = requests.post(url, data=data, headers=headers)
        response_data = json.loads(response.text)

        if response.status_code == 200 and response.text:
            access_token = response_data.get('access_token')
            error_message = ''
        else:
            access_token = ''
            # Probably something is wrong with Brightcove API, as all the data has been provided by a user, and
            # credentials (client_id and client_secret) have been previously fetched.
            # For dev purposes, response_data.get('error_description') may also be considered.
            error_message = "Authentication failed: no access token has been fetched.\n" \
                            "Please try again later."

        return access_token, error_message

    def authenticate_api(self, **kwargs):
        """
        Authenticates to a Brightcove API in order to perform authorized requests.
        Possible errors: https://docs.brightcove.com/en/perform/oauth-api/reference/error-messages.html

        Arguments:
            kwargs (dict): token and account_id key-value pairs
                as a platform-specific predefined client parameters, required to get credentials and access token.
        Returns:
            auth_data (dict): tokens and credentials, necessary to perform authorised API requests, and
            error_status_message (str) for verbosity.
        """
        token, account_id = kwargs.get('token'), kwargs.get('account_id')
        client_secret, client_id, error_message = self.get_client_credentials(token, account_id)
        if error_message:
            return {}, error_message
        access_token, error_message = self.get_access_token(client_id, client_secret)
        auth_data = {
            'client_secret': client_secret,
            'client_id': client_id,
            'access_token': access_token,
        }
        return auth_data, error_message

    def get_default_transcripts(self, **kwargs):
        """
        Fetches transcripts list from a video platform.

        Arguments:
            kwargs (dict): key-value pairs with account_id and video_id (both fetched from href field of studio editor),
                           and access_token (fetched from Brightcove API).
        Returns:
            default_transcripts (list): list of dicts of transcripts. Example:
                [
                    {
                        'lang': 'en',
                        'label': 'English',
                        'url': 'learning-services-media.brightcove.com/captions/bc_smart_ja.vtt'
                    },
                    # ...
                ]
            message (str): message for a user on default transcripts fetching.
        """
        video_id = kwargs.get('video_id')
        account_id = kwargs.get('account_id')  # TODO add handling: default account_id
        access_token = kwargs.get('access_token')
        url = self.captions_api['url'].format(account_id=account_id, media_id=video_id)
        authorisation_bearer = self.captions_api['authorised_request_header']['Authorization'].\
            format(access_token=access_token)
        headers = {'Authorization': authorisation_bearer}
        default_transcripts = []
        message = ''

        # Fetch available transcripts' languages and urls if authentication succeeded.
        try:
            data = requests.get('https://' + url, headers=headers)
            text = json.loads(data.text)
        except requests.exceptions.RequestException as exception:
            # Probably, current API has changed
            message = 'No timed transcript may be fetched from a video platform. ' \
                      'Error: {}'.format(str(exception))
            return default_transcripts, message

        if data.status_code == 200 and text:
            captions_data = text.get('text_tracks')
            # Handle empty response (no subs uploaded on a platform)
            if not captions_data:
                message = 'For now, video platform doesn\'t have any timed transcript for this video.'
                return default_transcripts, message
            transcripts_data = [
                [el.get('src'), el.get('srclang')]
                for el in captions_data
            ]
            # Populate default_transcripts
            for transcript_url, lang_code in transcripts_data:
                lang_label = self.get_transcript_language_parameters(lang_code)[1]
                default_transcript = {
                    'lang': lang_code,
                    'label': lang_label,
                    'url': transcript_url,
                }
                default_transcripts.append(default_transcript)
        # Permission denied; authentication message should be already generated.
        elif data.status_code == 401:
            message = ''
        else:
            try:
                message = str(text[0].get('message'))
            except AttributeError:
                message = 'No timed transcript may be fetched from a video platform. API response status: {}'.\
                    format(str(data.status_code))
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
