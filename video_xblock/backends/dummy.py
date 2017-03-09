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
    advanced_fields = ()

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
