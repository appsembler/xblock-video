"""
Wistia video XBlock provides a convenient way to place videos hosted on
Wistia platform.
All you need to provide is video url, this XBlock doest the rest for you.
"""

import pkg_resources
import re

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage

from django.template import Template, Context

from xblockutils.studio_editable import StudioEditableXBlockMixin

import HTMLParser

html_parser = HTMLParser.HTMLParser()

_ = lambda text: text

# From official Wistia documentation. May change in the future
# https://wistia.com/doc/construct-an-embed-code#the_regex
VIDEO_URL_RE = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/.*')

YOUTUBE_VIDEO_URL_RE = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/.*')


class VideoXBlock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        default='Wistia video',
        display_name=_('Component Display Name'),
        help=_('The name students see. This name appears in the course ribbon and as a header for the video.'),
        scope=Scope.settings,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page. E.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    editable_fields = ('display_name', 'href')

    @property
    def media_id(self):
        """
        Extracts Wistia's media hashed id from the media url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        if self.href:
            return self.href.split('/')[-1]
        return ''

    def validate_field_data(self, validation, data):
        if data.href == '':# and not VIDEO_URL_RE.match(data.href):
            validation.add(ValidationMessage(
                ValidationMessage.ERROR,
                _(u"Incorrect video url, please recheck")
            ))

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the WistiaVideoXBlock, shown to students
        when viewing courses.
        """
        if 'youtube' in self.href:
            # html = Template(self.resource_string("static/html/iframe_youtube.html"))
            html = Template(self.resource_string("static/html/youtube.html"))
            frag = Fragment(
                html_parser.unescape(
                    html.render(Context({'url': self.href}))
                )
            )

            html = self.resource_string('static/html/youtube.html')
            frag = Fragment(html)
            frag.add_css(self.resource_string(
                'static/bower_components/video.js/dist/video-js.min.css'
            ))
            frag.add_javascript(self.resource_string(
                'static/bower_components/video.js/dist/video.js'
            ))
            frag.add_javascript(
                self.resource_string(
                    'static/bower_components/videojs-youtube/dist/Youtube.js'
                )
            )
        else:
            html = self.resource_string('static/html/wistiavideo.html')
            frag = Fragment(html.format(self=self))
            frag.add_css(self.resource_string('static/css/wistiavideo.css'))
        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("WistiaVideoXBlock",
             """<wistiavideo media_id="ps0suympnl"/>
             """),
            ("WistiaVideoXBlock LMS",
             """<vertical_demo>
                <wistiavideo />
                <wistiavideo/>
                <wistiavideo/>
                </vertical_demo>
             """),
        ]
