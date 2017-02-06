"""
Vimeo Video player plugin
"""

import json
import re

from video_xblock import BaseVideoPlayer


class VimeoPlayer(BaseVideoPlayer):
    """
    VimeoPlayer is used for videos hosted on the Vimeo.com
    """

    # Regex is taken from http://regexr.com/3a2p0
    # https://vimeo.com/153979733
    url_re = re.compile(r'https?:\/\/(.+)?(vimeo.com)\/(?P<media_id>.*)')

    metadata_fields = []

    # Vimeo API for requesting transcripts.
    captions_api = {}

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        context['data_setup'] = json.dumps({
            "controlBar": {
                "volumeMenuButton": {
                    "inline": False,
                    "vertical": True
                }
            },
            "techOrder": ["vimeo"],
            "sources": [{
                "type": "video/vimeo",
                "src": context['url']
            }],
            "vimeo": {"iv_load_policy": 1},
            "controls": True,
            "preload": 'auto',
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time'],
                    "current_time": context['player_state']['current_time'],
                },
            }
        })

        frag = super(VimeoPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('../static/html/vimeo.html', **context)
        )

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-vimeo/src/Vimeo.js'
        ))

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-offset/dist/videojs-offset.min.js'
        ))

        return frag

    def authenticate_api(self, **kwargs):  # pylint: disable=unused-argument
        """
        Current Vimeo captions API doesn't require authentication, but this may change.
        """
        return {}, ''

    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        """
        Fetches transcripts list from a video platform.
        """
        # Fetch available transcripts' languages from API
        return [], ''

    def download_default_transcript(self, url):  # pylint: disable=unused-argument
        """
        Downloads default transcript in WebVVT format.

        Reference: https://git.io/vMK6W

        """
        return u''

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        """
        Customises display of studio editor fields per a video platform.
        """
        message = 'This field is to be disabled.'
        editable_fields = list(editable_fields)
        editable_fields.remove('account_id')
        editable_fields.remove('player_id')
        editable_fields.remove('token')
        customised_editable_fields = tuple(editable_fields)
        return message, customised_editable_fields
