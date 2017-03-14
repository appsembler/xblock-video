# -*- coding: utf-8 -*-
"""Html5 Video player plugin."""

import json
import re

from video_xblock import BaseVideoPlayer


class Html5Player(BaseVideoPlayer):
    """
    Html5Player is used for videos by providing direct URL.
    """

    url_re = url_re = re.compile(r'^(?P<protocol>https?|ftp)://[^\s/$.?#].[^\s]*.(?P<extension>mpeg|mp4|ogg|webm)')

    @property
    def advanced_fields(self):
        """
        Tuple of VideoXBlock fields to display in Advanced tab of edit modal window.

        Hide `download_video_url` field for Html5Player.
        """
        return [field for field in super(Html5Player, self).advanced_fields if field != 'download_video_url']

    # Html API for requesting transcripts.
    captions_api = {}

    def media_id(self, href):
        """
        Return unique value for video. Url is unique enough.
        """
        return href

    def get_type(self, href):
        """
        Get file extension for video.js type property.
        """
        return "video/" + self.url_re.search(href).group('extension')

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        data_setup = Html5Player.player_data_setup(context)
        data_setup['sources'][0]['type'] = self.get_type(context['url'])
        context['data_setup'] = json.dumps(data_setup)

        frag = super(Html5Player, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/html5.html', **context)
        )
        js_files = [
            'static/bower_components/videojs-offset/dist/videojs-offset.min.js',
            'static/js/player-context-menu.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @staticmethod
    def player_data_setup(context):
        """
        Html5 Player data setup.
        """
        result = BaseVideoPlayer.player_data_setup(context)
        result.update({
            "techOrder": ["html5"],
            "sources": [{
                "src": context['url']
            }],
            "playbackRates": [0.5, 1, 1.5, 2],
        })
        return result
