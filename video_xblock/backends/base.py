"""
Backend classes are responsible for video platform specific logic such as
validation, interaction with the platform via API and player rendering to end user.

Base Video player plugin
"""

import abc
import pkg_resources
import re

from HTMLParser import HTMLParser
from webob import Response
from xblock.fragment import Fragment
from xblock.plugin import Plugin

from django.template import Template, Context


html_parser = HTMLParser()  #pylint: disable=invalid-name


class BaseVideoPlayer(Plugin):
    """
    Inherit your video player class from this class
    """
    __metaclass__ = abc.ABCMeta

    entry_point = 'video_xblock.v1'

    @abc.abstractproperty
    def url_re(self):
        """
        Regex (list) to match video url

        Can be a regex object, a list of regex objects or a string.
        """
        return [] or re.compile('') or ''

    def get_frag(self, **context):
        """
        Returns a Fragment required to render video player on the client side.
        """
        frag = Fragment()
        frag.add_css(self.resource_string(
            '../static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_css(self.resource_string(
            '../static/css/videojs.css'
        ))
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        frag.add_css(self.resource_string(
            '../static/css/videojs-contextmenu-ui.css'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/video.js/dist/video.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-contextmenu/dist/videojs-contextmenu.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-contextmenu-ui/dist/videojs-contextmenu-ui.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/js/video-speed.js'
        ))
        frag.add_javascript(
            self.render_resource('../static/js/player_state.js', **context)
        )
        frag.add_javascript(self.render_resource(
            '../static/js/videojs-speed-handler.js', **context
        ))
        if context['player_state']['transcripts']:
            frag.add_javascript(self.resource_string(
                '../static/bower_components/videojs-transcript/dist/videojs-transcript.js'
            ))
            frag.add_javascript(
                self.render_resource('../static/js/videojs-transcript.js', **context)
            )
        frag.add_javascript(
            self.render_resource('../static/js/videojs-tabindex.js', **context)
        )
        frag.add_javascript(
            self.resource_string('../static/js/toggle-button.js')
        )
        frag.add_javascript(self.render_resource(
            '../static/js/videojs_event_plugin.js', **context
        ))

        return frag

    @abc.abstractmethod
    def media_id(self, href):
        """
        Extracts Platform's media id from the video url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """

        return ''

    def get_player_html(self, **context):
        """
        Renders self.get_frag as a html string and returns it as a Response.
        This method is used by VideoXBlock.render_player()

        Rendering sequence is set to JS must be in the head tag and executed
        before initializing video components.
        """
        frag = self.get_frag(**context)
        return Response(
            self.render_resource('../static/html/base.html', frag=frag),
            content_type='text/html'
        )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_resource(self, path, **context):
        """
        Renders static resource using provided context

        Returns: django.utils.safestring.SafeText
        """
        html = Template(self.resource_string(path))
        return html_parser.unescape(
            html.render(Context(context))
        )

    @classmethod
    def match(cls, href):
        """
        Checks if provided video `href` can be rendered by a video backend.

        `cls.url_re` attribute defined in subclassess are used for the check.
        """
        if isinstance(cls.url_re, list):
            return any(regex.search(href) for regex in cls.url_re)
        elif isinstance(cls.url_re, type(re.compile(''))):
            return cls.url_re.search(href)
        elif isinstance(cls.url_re, basestring):
            return re.search(cls.url_re, href, re.I)

    def add_js_content(self, path, **context):
        """
        Helper for adding javascript code inside <body> section.
        """
        return '<script>' + self.render_resource(path, **context) + '</script>'
