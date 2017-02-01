"""
Dummy Video player plugin
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
        return Fragment(u'[Here be Video]')

    def media_id(self, href):  # pylint: disable=unused-argument
        return '<media_id>'

    def captions_api(self):
        return {}

    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        return [], ''

    def download_default_transcript(self, url):  # pylint: disable=unused-argument
        return u''

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        return '', editable_fields

    def authenticate_api(self, **kwargs):  # pylint: disable=unused-argument
        return {}, ''
