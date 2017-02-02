"""
Backend classes are responsible for video platform specific logic such as
validation, interaction with the platform via API and player rendering to end user.

Base Video player plugin
"""

import abc
import re
from HTMLParser import HTMLParser
import pkg_resources

from webob import Response
from xblock.fragment import Fragment
from xblock.plugin import Plugin

from django.conf import settings
from django.template import Template, Context


html_parser = HTMLParser()  # pylint: disable=invalid-name


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

    @abc.abstractproperty
    def captions_api(self):
        """
        Dictionary of url, request parameters, and response structure of video platform's captions API.
        """
        return {}

    @abc.abstractproperty
    def metadata_fields(self):
        """
        List of keys (str) to be stored in the metadata xblock field.

        To keep xblock metadata field clean on it's each update,
        only backend-specific parameters should be stored in the field.

        Note: this is to add each new key (str) to be stored in metadata
        to the list being returned here.
        """
        return []

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
            frag.add_javascript(self.render_resource(
                '../static/js/transcript-download.js', **context
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
    def media_id(self, href):  # pylint: disable=unused-argument
        """
        Extracts Platform's media id from the video url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return ''

    @staticmethod
    @abc.abstractmethod
    def customize_xblock_fields_display(editable_fields):  # pylint: disable=unused-argument
        """
        Customises display of studio editor fields per a video platform.
        E.g. 'account_id' should be displayed for Brightcove only.

        Returns:
            client_token_help_message (str)
            editable_fields (tuple)
        """
        return '', ()

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
            return cls.url_re.search(href)  # pylint: disable=no-member
        elif isinstance(cls.url_re, basestring):
            return re.search(cls.url_re, href, re.I)

    def add_js_content(self, path, **context):
        """
        Helper for adding javascript code inside <body> section.
        """
        return '<script>' + self.render_resource(path, **context) + '</script>'

    @abc.abstractmethod
    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        """
        Fetches transcripts list from a video platform.

        Arguments:
            kwargs (dict): key-value pairs of API-specific identifiers (account_id, video_id, etc.) and tokens,
                necessary for API calls.
        Returns:
            list: List of dicts of transcripts. Example:
            [
                {
                    'lang': 'en',
                    'label': 'English',
                    'url': 'learning-services-media.brightcove.com/captions/bc_smart_ja.vtt'
                },
                # ...
            ]
            str: message for a user on default transcripts fetching.
        """
        return [], ''

    @abc.abstractmethod
    def authenticate_api(self, **kwargs):
        """
        Authenticates to a video platform's API in order to perform authorized requests.

        Arguments:
            kwargs (dict): platform-specific predefined client parameters, required to get credentials / tokens.
        Returns:
            auth_data (dict): tokens and credentials, necessary to perform authorised API requests, and
            error_status_message (str) for the sake of verbosity.
        """
        return {}, ''

    @abc.abstractmethod
    def download_default_transcript(self, url):  # pylint: disable=unused-argument
        """
        Downloads default transcript from a video platform API and uploads it to the video xblock.

        Arguments:
            url (str): transcript download url.
        Returns:
            unicode: Transcripts in WebVTT or SRT format.
        """
        return u''

    @staticmethod
    def get_transcript_language_parameters(lang_code):
        """
        Gets the parameters of a transcript's language, having checked on consistency with settings.

        Arguments:
            lang_code (str): raw language code of a transcript, fetched from the external sources.
        Returns:
            lang_code (str): pre-configured language code, e.g. 'br'
            lang_label (str): pre-configured language label, e.g. 'Breton'
        """
        # Delete region subtags; reference: https://github.com/edx/edx-platform/blob/master/lms/envs/common.py#L862
        lang_code = lang_code[0:2]
        # Check on consistency with the pre-configured ALL_LANGUAGES
        if lang_code not in [language[0] for language in settings.ALL_LANGUAGES]:
            raise Exception('Not all the languages of transcripts fetched from video platform are '
                            'consistent with the pre-configured ALL_LANGUAGES')
        lang_label = [language[1] for language in settings.ALL_LANGUAGES if language[0] == lang_code][0]
        return lang_code, lang_label

    @staticmethod
    def filter_default_transcripts(default_transcripts, transcripts):
        """
        Exclude enabled transcripts (fetched from API) from the list of available ones (fetched from video xblock)
        """
        enabled_languages_codes = [t[u'lang'] for t in transcripts]
        default_transcripts = [
            dt for dt in default_transcripts
            if (unicode(dt.get('lang')) not in enabled_languages_codes) and default_transcripts
        ]
        return default_transcripts
