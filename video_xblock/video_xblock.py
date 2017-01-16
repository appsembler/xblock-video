"""
Video XBlock provides a convenient way to embed videos hosted on
supported platforms into your course.
All you need to provide is video url, this XBlock does the rest for you.
"""

import datetime
import json
import logging
import os
import pkg_resources
import requests

from xblock.core import XBlock
from xblock.fields import Scope, Boolean, Integer, Float, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xmodule.fields import RelativeTime  # pylint: disable=import-error

from django.template import Template, Context
from pycaption import detect_format, WebVTTWriter
from webob import Response

from backends.base import BaseVideoPlayer, html_parser  # pylint: disable=relative-import
from settings import ALL_LANGUAGES  # pylint: disable=relative-import


_ = lambda text: text
log = logging.getLogger(__name__)


class TranscriptsMixin(XBlock):
    """
    TranscriptsMixin class to encapsulate transcripts-related logic
    """

    @staticmethod
    def convert_caps_to_vtt(caps):
        """
        Utility method converts any supported transcripts into WebVTT format.
        Supported input formats: DFXP/TTML - SAMI - SCC - SRT - WebVTT

        Arguments:
            caps (unicode): Raw transcripts.
        Returns:
            unicode: Transcripts converted into WebVTT format.
        """

        reader = detect_format(caps)
        if reader:
            return WebVTTWriter().write(reader().read(caps))
        else:
            return u''

    def route_transcripts(self, transcripts):
        """
        Re-routes non .vtt transcripts to `str_to_vtt` handler.
        """

        transcripts = json.loads(transcripts) if transcripts else []
        for tran in transcripts:
            if not tran['url'].endswith('.vtt'):
                tran['url'] = self.runtime.handler_url(
                    self, 'srt_to_vtt', query=tran['url']
                )
            yield tran

    @XBlock.handler
    def srt_to_vtt(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        Fetches raw transcripts, converts them into WebVTT format and returns back.

        Path to raw transcripts is passed in as `request.query_string`.

        Arguments:
            request (webob.Request): The request to handle
            suffix (string): The remainder of the url, after the handler url prefix, if available

        Returns:
            webob.Response: WebVTT transcripts wrapped in Response object.
        """
        caps_path = request.query_string
        caps = requests.get(request.host_url + caps_path).text
        return Response(self.convert_caps_to_vtt(caps))


class VideoXBlock(TranscriptsMixin, StudioEditableXBlockMixin, XBlock):
    """
    Main VideoXBlock class.
    Responsible for saving video settings and rendering it for students.
    """

    icon_class = "video"

    display_name = String(
        default=_('Video'),
        display_name=_('Component Display Name'),
        help=_('The name students see. This name appears in the course ribbon and as a header for the video.'),
        scope=Scope.content,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page. E.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    account_id = String(
        default='',
        display_name=_('Account Id'),
        help=_('Your Brightcove account id'),
        scope=Scope.content,
    )

    player_id = String(
        default='default',
        display_name=_('Player Id'),
        help=_('Your Brightcove player id. Use "Luna" theme for all your players. You can choose one of your players'
               ' from a <a href="https://studio.brightcove.com/products/videocloud/players" target="_blank">list</a>.'),
        scope=Scope.content,
    )

    player_name = String(
        default='dummy-player',
        scope=Scope.content
    )

    start_time = RelativeTime(  # datetime.timedelta object
        help=_(
            "Time you want the video to start if you don't want the entire video to play. "
            "Not supported in the native mobile app: the full video file will play. "
            "Formatted as HH:MM:SS. The maximum value is 23:59:59."
        ),
        display_name=_("Video Start Time"),
        scope=Scope.content,
        default=datetime.timedelta(seconds=0)
    )
    end_time = RelativeTime(  # datetime.timedelta object
        help=_(
            "Time you want the video to stop if you don't want the entire video to play. "
            "Not supported in the native mobile app: the full video file will play. "
            "Formatted as HH:MM:SS. The maximum value is 23:59:59."
        ),
        display_name=_("Video Stop Time"),
        scope=Scope.content,
        default=datetime.timedelta(seconds=0)
    )

    # Playback state fields
    current_time = Integer(
        default=0,
        scope=Scope.user_state,
        help='Seconds played back after the start'
    )

    playback_rate = Float(
        default=1,
        scope=Scope.preferences,
        help='Supported video playbacks speeds are: 0.5, 1, 1.5, 2'
    )

    volume = Float(
        default=1,
        scope=Scope.preferences,
        help='Video volume: from 0 to 1'
    )

    muted = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Video is muted or not"
    )

    captions_language = String(
        default='',
        scope=Scope.preferences,
        help="ISO code current language for captions and transcripts"
    )

    transcripts_enabled = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Transcripts is enabled or not"
    )

    captions_enabled = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Captions is enabled or not"
    )

    handout = String(
        default='',
        scope=Scope.content,
        display_name=_('Upload handout'),
        help=_('You can upload handout file for students')
    )

    transcripts = String(
        default='',
        scope=Scope.content,
        display_name=_('Upload transcript'),
        help=_(
            'Add transcripts in different languages. Click below to specify a language and upload an .srt transcript'
            ' file for that language.'
        )
    )

    download_transcript_allowed = Boolean(
        default=False,
        scope=Scope.content,
        display_name=_('Download Transcript Allowed'),
        help=_(
            "Allow students to download the timed transcript. A link to download the file appears below the video."
            " By default, the transcript is an .vtt or .srt file. If you want to provide the transcript for download"
            " in a different format, upload a file by using the Upload Handout field."
        )
    )

    editable_fields = (
        'display_name', 'href', 'start_time', 'end_time', 'account_id',
        'player_id', 'handout', 'transcripts', 'download_transcript_allowed'
    )
    player_state_fields = (
        'current_time', 'muted', 'playback_rate', 'volume',
        'transcripts_enabled', 'captions_enabled', 'captions_language'
    )

    @property
    def player_state(self):
        """
        Returns video player state as a dictionary
        """
        course = self.runtime.modulestore.get_course(self.course_id)
        return {
            'current_time': self.current_time,
            'muted': self.muted,
            'playback_rate': self.playback_rate,
            'volume': self.volume,
            'transcripts': json.loads(self.transcripts) if self.transcripts else [],
            'transcripts_enabled': self.transcripts_enabled,
            'captions_enabled': self.captions_enabled,
            'captions_language': self.captions_language or course.language
        }

    @staticmethod
    def get_brightcove_js_url(account_id, player_id):
        """
        Returns url to brightcove player js file considering account_id and player_id
        """
        return "https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
            account_id=account_id,
            player_id=player_id
        )

    @player_state.setter
    def player_state(self, state):
        """
        Saves video player state passed in as a dict into xblock's fields
        """
        self.current_time = state.get('current_time', self.current_time)
        self.muted = state.get('muted', self.muted)
        self.playback_rate = state.get('playback_rate', self.playback_rate)
        self.volume = state.get('volume', self.volume)
        self.transcripts = state.get('transcripts', self.transcripts)
        self.transcripts_enabled = state.get('transcripts_enabled', self.transcripts_enabled)
        self.captions_enabled = state.get('captions_enabled', self.captions_enabled)
        self.captions_language = state.get('captions_language', self.captions_language)

    def validate_field_data(self, validation, data):
        """
        Validate data submitted via xblock edit pop-up
        """
        if data.account_id and data.player_id:
            try:
                response = requests.head(VideoXBlock.get_brightcove_js_url(data.account_id, data.player_id))
                if response.status_code != 200:
                    validation.add(ValidationMessage(
                        ValidationMessage.ERROR,
                        _(u"Invalid Player Id, please recheck")
                    ))
            except requests.ConnectionError:
                validation.add(ValidationMessage(
                    ValidationMessage.ERROR,
                    _(u"Can't validate submitted player id at the moment. Please try to save settings one more time.")
                ))

        if data.href == '':
            return
        for _player_name, player_class in BaseVideoPlayer.load_classes():
            if player_class.match(data.href):
                return

        validation.add(ValidationMessage(
            ValidationMessage.ERROR,
            _(u"Incorrect or unsupported video URL, please recheck.")
        ))

    def resource_string(self, path):
        """
        Handy helper for getting resources from our kit.
        """
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

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the VideoXBlock, shown to students
        when viewing courses.
        """

        player_url = self.runtime.handler_url(self, 'render_player')
        transcript_download_link = self.get_transcript_download_link()
        download_transcript_handler_url = self.runtime.handler_url(self, 'download_transcript')
        frag = Fragment(
            self.render_resource(
                'static/html/student_view.html',
                player_url=player_url,
                display_name=self.display_name,
                usage_id=self.location.to_deprecated_string(),  # pylint: disable=no-member
                handout=self.handout,
                transcripts=self.route_transcripts(self.transcripts),
                download_transcript_allowed=self.download_transcript_allowed,
                handout_file_name=self.get_file_name_from_path(self.handout),
                transcript_download_link=transcript_download_link,
                download_transcript_handler_url=download_transcript_handler_url
            )
        )
        frag.add_javascript(self.resource_string("static/js/video_xblock.js"))
        frag.add_css(self.resource_string("static/css/handout.css"))
        frag.initialize_js('VideoXBlockStudentViewInit')
        return frag

    def studio_view(self, context):  # pylint: disable=unused-argument
        """
        Render a form for editing this XBlock
        """
        fragment = Fragment()
        languages = [{'label': label, 'code': lang} for lang, label in ALL_LANGUAGES]
        languages.sort(key=lambda l: l['label'])
        transcripts = json.loads(self.transcripts) if self.transcripts else []
        download_transcript_handler_url = self.runtime.handler_url(self, 'download_transcript')
        context = {
            'fields': [],
            'courseKey': self.location.course_key,  # pylint: disable=no-member
            'languages': languages,
            'transcripts': transcripts,
            'download_transcript_handler_url': download_transcript_handler_url
        }
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)

        fragment.content = self.render_resource('static/html/studio_edit.html', **context)
        fragment.add_css(self.resource_string("static/css/handout.css"))
        fragment.add_css(self.resource_string("static/css/transcripts.css"))
        fragment.add_css(self.resource_string("static/css/studio-edit.css"))
        fragment.add_javascript(self.resource_string("static/js/studio-edit.js"))
        fragment.initialize_js('StudioEditableXBlock')
        return fragment

    @XBlock.handler
    def render_player(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        student_view() loads this handler as an iframe to display actual
        video player.
        """
        player = self.get_player()
        save_state_url = self.runtime.handler_url(self, 'save_player_state')
        transcripts = self.render_resource(
            'static/html/transcripts.html',
            transcripts=self.route_transcripts(self.transcripts)
        )
        return player.get_player_html(
            url=self.href, autoplay=False, account_id=self.account_id, player_id=self.player_id,
            video_id=player.media_id(self.href),
            video_player_id='video_player_{}'.format(self.location.block_id),  # pylint: disable=no-member
            save_state_url=save_state_url,
            player_state=self.player_state,
            start_time=int(self.start_time.total_seconds()),
            end_time=int(self.end_time.total_seconds()),
            brightcove_js_url=VideoXBlock.get_brightcove_js_url(self.account_id, self.player_id),
            transcripts=transcripts
        )

    @XBlock.json_handler
    def save_player_state(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        XBlock handler to save playback player state.
        Called by student_view's JavaScript
        """
        player_state = {
            'current_time': request['currentTime'],
            'playback_rate': request['playbackRate'],
            'volume': request['volume'],
            'muted': request['muted'],
            'transcripts': self.transcripts,
            'transcripts_enabled': request['transcriptsEnabled'],
            'captions_enabled': request['captionsEnabled'],
            'captions_language': request['captionsLanguage']
        }
        self.player_state = player_state
        return {'success': True}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Handler to publish XBlock event from frontend.
        Called by student_view's JavaScript
        """
        try:
            eventType = data.pop('eventType')  # pylint: disable=invalid-name
        except KeyError:
            return {'result': 'error', 'message': 'Missing eventType in JSON data'}

        self.runtime.publish(self, eventType, data)
        return {'result': 'success'}

    def clean_studio_edits(self, data):
        """
        Given POST data dictionary 'data', clean the data before validating it.

        Tries to detect player by submitted video url. If fails, it defaults to 'dummy-player'
        """
        data['player_name'] = self.fields['player_name'].default
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_name == 'dummy-player':
                continue
            if player_class.match(data['href']):
                data['player_name'] = player_name

    def get_player(self):
        """
        Helper method to load video player by entry-point label
        """
        player = BaseVideoPlayer.load_class(self.player_name)
        return player()

    def _make_field_info(self, field_name, field):
        """
        Overrides and extends data of built-in method
        """
        if field_name in ('start_time', 'end_time'):
            # RelativeTime field doesn't supported by default.
            return {
                'name': field_name,
                'display_name': _(field.display_name) if field.display_name else "",  # pylint: disable=translation-of-non-string
                'is_set': field.is_set_on(self),
                'default': field.default,
                'value': field.read_from(self),
                'has_values': False,
                'help': _(field.help) if field.help else "",  # pylint: disable=translation-of-non-string
                'allow_reset': field.runtime_options.get('resettable_editor', True),
                'list_values': None,
                'has_list_values': False,
                'type': 'string',
            }
        info = super(VideoXBlock, self)._make_field_info(field_name, field)
        if field_name == 'handout':
            info['type'] = 'file_uploader'
            info['file_name'] = self.get_file_name_from_path(self.handout)
            info['value'] = self.get_path_for(self.handout)
        if field_name == 'transcripts':
            info['type'] = 'transcript_uploader'
        return info

    def get_file_name_from_path(self, field):
        """
        Helper for getting filename from string with path to mongoDB storage.
        Example of string:
            asset-v1-RaccoonGang+1+2018+type@asset+block@<filename>

        Args:
            field: The path to file.

        Returns:
            The name of file with an extension.
        """
        return field.split('@')[-1]

    def get_path_for(self, file_field):
        """
        Url retrieved after storing file field in mongoDB look like this:
            'asset-v1-RaccoonGang+1+2018+type@asset+block@<filename>'
        Returns downloaded asset url with slash in start of it
        """
        if file_field:
            return os.path.join('/', file_field)
        return ''

    def get_transcript_download_link(self):
        """
        Returns link for downloading transcript of the current captions language if it exists
        """
        transcripts = json.loads(self.transcripts) if self.transcripts else []
        for transcript in transcripts:
            if transcript.get('lang') == self.captions_language:
                return transcript.get('url')
        return '#'

    @XBlock.handler
    def download_transcript(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        Function for downloading a transcripts.
        Returns:
            The file with the correct name
        """
        trans_path = self.get_path_for(request.query_string)
        result = requests.get(request.host_url + request.query_string).text
        filename = self.get_file_name_from_path(trans_path)
        response = Response(result)
        headerlist = [
            ('Content-Type', 'text/plain'),
            ('Content-Disposition', 'attachment; filename={}'.format(filename))
        ]
        response.headerlist = headerlist
        return response
