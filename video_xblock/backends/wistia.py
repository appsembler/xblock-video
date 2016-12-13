import json
import re

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
                "xblockEventPlugin": {}
            }
        })

        frag = super(WistiaPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('../static/html/wistiavideo.html', **context)
        )
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-wistia/src/wistia.js'
        ))

        return frag
