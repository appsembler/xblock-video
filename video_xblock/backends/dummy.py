"""
Dummy Video player plugin.
"""

import re

from xblock.fragment import Fragment
from video_xblock import BaseVideoPlayer


class DummyPlayer(BaseVideoPlayer):
    """
    DummyPlayer is a placeholder for cases when appropriate player can't be displayed.
    """

    url_re = re.compile(r'')
    metadata_fields = []

    def get_frag(self, **context):  # pylint: disable=unused-argument
        """
        Return a Fragment required to render video player on the client side.
        """
        return Fragment(u'[Here be Video]')

    def media_id(self, href):  # pylint: disable=unused-argument
        """
        Extract Platform's media id from the video url.
        """
        return '<media_id>'

    def captions_api(self):
        """
        Dictionary of url, request parameters, and response structure of video platform's captions API.
        """
        return {}

    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        """
        Fetch transcripts list from a video platform.
        """
        return [], ''

    def download_default_transcript(self, url, language_code):  # pylint: disable=unused-argument
        """
        Download default transcript from a video platform API and formats it accordingly to the WebVTT standard.

        Arguments:
            url (str): API url to fetch a default transcript from.
            language_code (str): Language code of a default transcript to be downloaded.
        """
        return u''

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        """
        Customise display of studio editor fields per video platform.
        """
        return '', editable_fields

    def authenticate_api(self, **kwargs):  # pylint: disable=unused-argument
        """
        Authenticate to a video platform's API in order to perform authorized requests.
        """
        return {}, ''
