"""
Video XBlock provides a convenient way to embed videos hosted on
supported platforms into your course.
All you need to provide is video url, this XBlock does the rest for you.
"""

import logging
import pkg_resources
import json
import os

from xblock.core import XBlock
from xblock.fields import Scope, Boolean, Integer, Float, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin

from django.template import Template, Context

from backends.base import BaseVideoPlayer, html_parser
from . import settings


_ = lambda text: text
log = logging.getLogger(__name__)


class VideoXBlock(StudioEditableXBlockMixin, XBlock):
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
        help=_('Your Brightcove player id. Use "Luna" theme for all your players'),
        scope=Scope.content,
    )

    player_name = String(
        default='dummy-player',
        scope=Scope.content
    )

    # Playback state fields
    current_time = Integer(
        default=0,
        scope=Scope.user_state,
        help=_('Seconds played back from the start')
    )

    playback_rate = Float(
        default=1,
        scope=Scope.preferences,
        help=_('Video playback speed: 0.5, 1, 1.5, 2')
    )

    volume = Float(
        default=1,
        scope=Scope.preferences,
        help=_('Video volume: from 0 to 1')
    )

    muted = Boolean(
        default=False,
        scope=Scope.preferences,
        help=_("Video muted or not")
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
        help=_('Add transcripts in different languages. Click below to specify a language and upload an .srt transcript file for that language.')
    )

    editable_fields = ('display_name', 'href', 'account_id', 'handout', 'transcripts', 'player_id')
    player_state_fields = ('current_time', 'muted', 'playback_rate', 'volume')

    @property
    def player_state(self):
        """
        Returns video player state as a dictionary
        """
        return {
            'current_time': self.current_time,
            'muted': self.muted,
            'playback_rate': self.playback_rate,
            'volume': self.volume,
            'transcripts': json.loads(self.transcripts) if self.transcripts else [],
        }

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

    def validate_field_data(self, validation, data):
        """
        Validate data submitted via xblock edit pop-up
        """

        if data.href == '':
            return
        for player_name, player_class in BaseVideoPlayer.load_classes():
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

    def student_view(self, context=None):
        """
        The primary view of the VideoXBlock, shown to students
        when viewing courses.
        """

        player_url = self.runtime.handler_url(self, 'render_player')
        frag = Fragment(
            self.render_resource(
                'static/html/student_view.html',
                player_url=player_url,
                display_name=self.display_name,
                usage_id=self.location.to_deprecated_string(),
                handout=self.handout,
                handout_file_name=self.get_handout_file_name()
            )
        )
        frag.add_javascript(self.resource_string("static/js/video_xblock.js"))
        frag.add_css(self.resource_string("static/css/handout.css"))
        frag.initialize_js('VideoXBlockStudentViewInit')
        return frag

    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        fragment = Fragment()
        languages = [{'label': label, 'code': lang} for lang, label in settings.ALL_LANGUAGES]
        languages.sort(key=lambda l: l['label'])
        transcripts = json.loads(self.transcripts) if self.transcripts else []
        context = {
            'fields': [],
            'courseKey': self.location.course_key,
            'languages': languages,
            'transcripts': transcripts
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
        path_to_images = self.runtime.local_resource_url(self, 'public/images/')
        path_to_fonts = self.runtime.local_resource_url(self, 'public/fonts/')

        fragment.content = self.render_resource('static/html/studio_edit.html', **context)
        fragment.add_css(self.resource_string("static/css/handout.css"))
        fragment.add_css(self.resource_string("static/css/transcripts.css"))
        fragment.add_css(self.render_resource("static/css/studio-main-v1.css",
            path_to_images=path_to_images,
            path_to_fonts=path_to_fonts
            )
        )
        fragment.add_javascript(self.resource_string("static/js/studio_edit.js"))
        fragment.initialize_js('StudioEditableXBlock')
        return fragment

    @XBlock.handler
    def render_player(self, request, suffix=''):
        """
        student_view() loads this handler as an iframe to display actual
        video player.
        """
        player = self.get_player()
        save_state_url = self.runtime.handler_url(self, 'save_player_state')
        return player.get_player_html(
            url=self.href, autoplay=False, account_id=self.account_id, player_id=self.player_id,
            video_id=player.media_id(self.href),
            video_player_id='video_player_{}'.format(self.location.block_id),
            save_state_url=save_state_url,
            player_state=self.player_state
        )

    @XBlock.json_handler
    def save_player_state(self, request, suffix=''):
        """
        XBlock handler to save playback player state.
        Called by student_view's JavaScript
        """
        player_state = {
            'current_time': request['currentTime'],
            'playback_rate': request['playbackRate'],
            'volume': request['volume'],
            'muted': request['muted'],
            'transcripts': self.transcripts
        }
        self.player_state = player_state
        return {'success': True}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        """
        Handler to publish XBlock event from frontend.
        Called by student_view's JavaScript
        """
        try:
            eventType = data.pop('eventType')
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
        info = super(VideoXBlock, self)._make_field_info(field_name, field)
        if field_name == 'handout':
            info['type'] = 'file_uploader'
            info['file_name'] = self.get_handout_file_name()
            info['value'] = self.get_url_for(self.handout)
        if field_name == 'transcripts':
            info['type'] = 'transcript_uploader'
        return info

    def get_handout_file_name(self):
        """
        Field handout look like this:
        asset-v1-RaccoonGang+1+2018+type@asset+block@<filename>

        It returns only name of file with extension
        """
        return self.handout.split('@')[-1]

    def get_url_for(self, field):
        """
        Returns downloaded asset url
        """
        if field:
            return os.path.join('/', field)
        return ''
