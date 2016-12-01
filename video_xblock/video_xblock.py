"""
Video XBlock provides a convenient way to embed videos hosted on
supported platforms into your course.
All you need to provide is video url, this XBlock does the rest for you.
"""

import logging
import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Boolean, Integer, Float, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin

from django.template import Template, Context

from backends.base import BaseVideoPlayer, html_parser


_ = lambda text: text
log = logging.getLogger(__name__)


class VideoXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Main VideoXBlock class.
    Responsible for saving video settings and rendering it for students.
    """

    icon_class = "video"

    display_name = String(
        default='Video',
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

    player_name = String(
        default='dummy-player',
        scope=Scope.content
    )

    # Playback state fields
    current_time = Integer(
        default=0,
        scope=Scope.user_state,
        help='Seconds played back from the start'
    )

    playback_rate = Float(
        default=1,
        scope=Scope.preferences,
        help='Video playback speed: 0.5, 1, 1.5, 2'
    )

    volume = Float(
        default=1,
        scope=Scope.preferences,
        help='Video volume: from 0 to 1'
    )

    muted = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Video muted or not"
    )

    editable_fields = ('display_name', 'href', 'account_id')
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
            'volume': self.volume
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
                usage_id=self.location.to_deprecated_string()
            )
        )
        frag.add_javascript(self.resource_string("static/js/video_xblock.js"))
        frag.initialize_js('VideoXBlockStudentViewInit')
        return frag

    @XBlock.handler
    def render_player(self, request, suffix=''):
        """
        student_view() loads this handler as an iframe to display actual
        video player.
        """
        player = self.get_player()
        save_state_url = self.runtime.handler_url(self, 'save_player_state')
        return player.get_player_html(
            url=self.href, autoplay=False, account_id=self.account_id,
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
            'muted': request['muted']
        }
        self.player_state = player_state
        return {'success': True}

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
