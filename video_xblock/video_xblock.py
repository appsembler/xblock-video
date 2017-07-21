"""
Video XBlock provides a convenient way to embed videos hosted on supported platforms into your course.

All you need to provide is video url, this XBlock does the rest for you.
"""

import datetime
import httplib
import json
import logging
import os.path

import requests
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, Boolean, String, Dict
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin

from . import __version__
from .backends.base import BaseVideoPlayer
from .constants import PlayerName, TranscriptSource
from .exceptions import ApiClientError
from .fields import RelativeTime
from .mixins import ContentStoreMixin, LocationMixin, PlaybackStateMixin, SettingsMixin, TranscriptsMixin
from .settings import ALL_LANGUAGES
from .utils import (
    create_reference_name, filter_transcripts_by_source, normalize_transcripts,
    render_resource, render_template, resource_string, ugettext as _,
)
from .workbench.mixin import WorkbenchMixin

log = logging.getLogger(__name__)


class VideoXBlock(
        SettingsMixin, TranscriptsMixin, PlaybackStateMixin, LocationMixin,
        StudioEditableXBlockMixin, ContentStoreMixin, WorkbenchMixin, XBlock
):
    """
    Main VideoXBlock class, responsible for saving video settings and rendering it for students.

    VideoXBlock only provide a storage facilities for fields data, but not
    decide what fields to show to user. `BaseVideoPlayer` and it's subclassess
    declare what fields are required for proper configuration of a video.
    See `BaseVideoPlayer.basic_fields` and `BaseVideoPlayer.advanced_fields`.
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

    download_video_allowed = Boolean(
        default=False,
        scope=Scope.content,
        display_name=_('Video Download Allowed'),
        help=_(
            "Allow students to download this video if they cannot use the edX video player."
            " A link to download the file appears below the video."
        ),
        resettable_editor=False
    )

    download_video_url = String(
        default='',
        display_name=_('Video file URL'),
        help=_("The URL where you've posted non hosted versions of the video. URL must end in .mpeg, .mp4, .ogg, or"
               " .webm. (For browser compatibility, we strongly recommend .mp4 and .webm format.) To allow students to"
               " download these videos, set Video Download Allowed to True."),
        scope=Scope.content
    )

    account_id = String(
        default='default',
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
        default=PlayerName.DUMMY,
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

    handout = String(
        default='',
        scope=Scope.content,
        display_name=_('Upload handout'),
        help=_('You can upload handout file for students')
    )

    download_transcript_allowed = Boolean(
        default=False,
        scope=Scope.content,
        display_name=_('Download Transcript Allowed'),
        help=_(
            "Allow students to download the timed transcript. A link to download the file appears below the video."
            " By default, the transcript is an .vtt or .srt file. If you want to provide the transcript for download"
            " in a different format, upload a file by using the Upload Handout field."
        ),
        resettable_editor=False
    )

    default_transcripts = String(
        default='',
        scope=Scope.content,
        display_name=_('Default Timed Transcript'),
        help=_(
            'Default transcripts are uploaded automatically from a video platform '
            'to the list of available transcripts.<br/>'
            '<b>Note: valid "Video API Token" should be given in order to make auto fetching possible.</b><br/>'
            'Advice: disable transcripts displaying on your video service to avoid transcripts overlapping.'
        ),
        resettable_editor=False
    )

    token = String(
        default='',
        display_name=_('Video API Token'),
        help=_('You can generate a client token following official documentation of your video platform\'s API.'),
        scope=Scope.content,
        resettable_editor=False
    )

    metadata = Dict(
        default={},
        display_name=_('Metadata'),
        help=_('This field stores different metadata, e.g. authentication data. '
               'If new metadata item is designed, this is to add an appropriate key to backend\'s '
               '`metadata_fields` property.'),
        scope=Scope.content
    )

    @property
    def editable_fields(self):
        """
        Return list of xblock's editable fields used by StudioEditableXBlockMixin.clean_studio_edits().
        """
        return self.get_player().editable_fields

    @staticmethod
    def get_brightcove_js_url(account_id, player_id):
        """
        Return url to brightcove player js file, considering `account_id` and `player_id`.

        Arguments:
            account_id (str): Account id fetched from video xblock.
            player_id (str): Player id fetched from video xblock.
        Returns:
            Url to brightcove player js (str).
        """
        return "https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
            account_id=account_id,
            player_id=player_id
        )

    @staticmethod
    def add_validation_message(validation, message_text):
        """
        Add error message on xblock fields validation.

        Attributes:
            validation (xblock.validation.Validation): Object containing validation information for an xblock instance.
            message_text (unicode): Message text per se.
        """
        validation.add(ValidationMessage(ValidationMessage.ERROR, message_text))

    def validate_account_id_data(self, validation, data):
        """
        Validate account id value which is mandatory.

        Attributes:
            validation (xblock.validation.Validation): Object containing validation information for an xblock instance.
            data (xblock.internal.VideoXBlockWithMixins): Object containing data on xblock.
        """
        is_provided_account_id = \
            data.account_id != self.fields['account_id'].default  # pylint: disable=unsubscriptable-object
        # Validate provided account id
        if is_provided_account_id:
            try:
                response = requests.head(VideoXBlock.get_brightcove_js_url(data.account_id, data.player_id))
                if response.status_code != httplib.OK:
                    self.add_validation_message(validation, _(u"Invalid Account Id, please recheck."))
            except requests.ConnectionError:
                self.add_validation_message(
                    validation,
                    _(u"Can't validate submitted account id at the moment. "
                      u"Please try to save settings one more time.")
                )
        # Account Id field is mandatory
        else:
            self.add_validation_message(
                validation,
                _(u"Account Id can not be empty. Please provide a valid Brightcove Account Id.")
            )

    def validate_href_data(self, validation, data):
        """
        Validate href value.

        Attributes:
            validation (xblock.validation.Validation): Object containing validation information for an xblock instance.
            data (xblock.internal.VideoXBlockWithMixins): Object containing data on xblock.
        """
        is_not_provided_href = \
            data.href == self.fields['href'].default  # pylint: disable=unsubscriptable-object
        is_matched_href = False
        for _player_name, player_class in BaseVideoPlayer.load_classes():
            if player_class.match(data.href):
                is_matched_href = True
        # Validate provided video href value
        if not (is_not_provided_href or is_matched_href):
            self.add_validation_message(
                validation,
                _(u"Incorrect or unsupported video URL, please recheck.")
            )

    def validate_field_data(self, validation, data):
        """
        Validate data submitted via xblock edit pop-up.

        Reference:
            https://github.com/edx/xblock-utils/blob/v1.0.3/xblockutils/studio_editable.py#L245

        Attributes:
            validation (xblock.validation.Validation): Object containing validation information for an xblock instance.
            data (xblock.internal.VideoXBlockWithMixins): Object containing data on xblock.
        """
        is_brightcove = str(self.player_name) == PlayerName.BRIGHTCOVE

        if is_brightcove:
            self.validate_account_id_data(validation, data)

        self.validate_href_data(validation, data)

    def get_download_video_url(self):
        """
        Return direct video url for download if download is allowed.

        Else return `False` which will hide "download video" button.
        """
        return self.download_video_allowed and self.get_player().download_video_url

    def student_view(self, _context=None):
        """
        The primary view of the `VideoXBlock`, shown to students when viewing courses.
        """
        player_url = self.runtime.handler_url(self, 'render_player')
        download_transcript_handler_url = self.runtime.handler_url(self, 'download_transcript')
        transcript_download_link = self.get_transcript_download_link()
        full_transcript_download_link = ''

        if transcript_download_link:
            full_transcript_download_link = download_transcript_handler_url + transcript_download_link
        frag = Fragment(
            render_resource(
                'static/html/student_view.html',
                player_url=player_url,
                display_name=self.display_name,
                usage_id=self.usage_id,
                handout=self.handout,
                transcripts=self.route_transcripts(),
                download_transcript_allowed=self.download_transcript_allowed,
                transcripts_streaming_enabled=self.threeplaymedia_streaming,
                download_video_url=self.get_download_video_url(),
                handout_file_name=self.get_file_name_from_path(self.handout),
                transcript_download_link=full_transcript_download_link,
                version=__version__,
            )
        )
        frag.add_javascript(resource_string("static/js/student-view/video-xblock.js"))
        frag.add_css(resource_string("static/css/student-view.css"))
        frag.initialize_js('VideoXBlockStudentViewInit')
        return frag

    def _update_default_transcripts(self, player, transcripts):
        """
        Private method to fetch/update default transcripts.
        """
        log.debug("Default transcripts updating...")
        # Prepare parameters necessary to make requests to API.
        video_id = player.media_id(self.href)
        kwargs = {'video_id': video_id}
        for k in self.metadata:
            kwargs[k] = self.metadata[k]
        # For a Brightcove player only
        is_not_default_account_id = \
            self.account_id is not self.fields['account_id'].default  # pylint: disable=unsubscriptable-object
        if is_not_default_account_id:
            kwargs['account_id'] = self.account_id

        # Fetch captions list (available/default transcripts list) from video platform API
        try:
            default_transcripts, transcripts_autoupload_message = player.get_default_transcripts(**kwargs)
        except ApiClientError:
            default_transcripts, transcripts_autoupload_message = [], _('Failed to fetch default transcripts.')
        log.debug("Autofetch message: '{}'".format(transcripts_autoupload_message))
        # Default transcripts should contain transcripts of distinct languages only
        distinct_default_transcripts = player.clean_default_transcripts(default_transcripts)
        # Needed for frontend
        initial_default_transcripts = distinct_default_transcripts
        # Exclude enabled transcripts from the list of available ones, and remove duplicates
        filtered_default_transcripts = player.filter_default_transcripts(distinct_default_transcripts, transcripts)
        self.default_transcripts = filtered_default_transcripts
        if self.default_transcripts:
            self.default_transcripts.sort(key=lambda l: l['label'])

        return initial_default_transcripts, transcripts_autoupload_message

    def studio_view(self, _context):
        """
        Render a form for XBlock editing.
        """
        fragment = Fragment()
        player = self.get_player()
        languages = [{'label': label, 'code': lang} for lang, label in ALL_LANGUAGES]
        languages.sort(key=lambda l: l['label'])
        transcripts = self.get_enabled_transcripts()
        download_transcript_handler_url = self.runtime.handler_url(self, 'download_transcript')
        auth_error_message = ''
        # Authenticate to API of the player video platform and update metadata with auth information.
        # Note that there is no need to authenticate to Youtube API,
        # whilst for Wistia, a sample authorised request is to be made to ensure authentication succeeded,
        # since it is needed for the auth status message generation and the player's state update with auth status.
        if self.token:
            _auth_data, auth_error_message = self.authenticate_video_api(self.token.encode(encoding='utf-8'))

        initial_default_transcripts, transcripts_autoupload_message = self._update_default_transcripts(
            player, transcripts
        )

        # Prepare basic_fields and advanced_fields for them to be rendered
        basic_fields = self.prepare_studio_editor_fields(player.basic_fields)
        advanced_fields = self.prepare_studio_editor_fields(player.advanced_fields)
        log.debug("Fetched default transcripts: {}".format(initial_default_transcripts))
        context = {
            'advanced_fields': advanced_fields,
            'auth_error_message': auth_error_message,
            'basic_fields': basic_fields,
            'courseKey': self.course_key,
            'languages': languages,
            'player_name': self.player_name,  # for players identification
            'players': PlayerName,
            'sources': TranscriptSource.to_dict().items(),
            # transcripts context:
            'transcripts': transcripts,
            'transcripts_fields': self.prepare_studio_editor_fields(player.trans_fields),
            'three_pm_fields': self.prepare_studio_editor_fields(player.three_pm_fields),
            'transcripts_type': '3PM' if self.threeplaymedia_streaming else 'manual',
            'default_transcripts': self.default_transcripts,
            'enabled_default_transcripts': filter_transcripts_by_source(transcripts),
            'initial_default_transcripts': initial_default_transcripts,
            'transcripts_autoupload_message': transcripts_autoupload_message,
            'download_transcript_handler_url': download_transcript_handler_url,
        }

        fragment.content = render_template('studio-edit.html', **context)
        fragment.add_css(resource_string("static/css/student-view.css"))
        fragment.add_css(resource_string("static/css/transcripts-upload.css"))
        fragment.add_css(resource_string("static/css/studio-edit.css"))
        fragment.add_css(resource_string("static/css/studio-edit-accordion.css"))
        fragment.add_javascript(resource_string("static/js/runtime-handlers.js"))
        fragment.add_javascript(resource_string("static/js/studio-edit/utils.js"))
        fragment.add_javascript(resource_string("static/js/studio-edit/studio-edit.js"))
        fragment.add_javascript(resource_string("static/js/studio-edit/transcripts-autoload.js"))
        fragment.add_javascript(resource_string("static/js/studio-edit/transcripts-manual-upload.js"))
        fragment.initialize_js('StudioEditableXBlock')
        return fragment

    @XBlock.handler
    def render_player(self, _request, _suffix=''):
        """
        View `student_view` loads this handler as an iframe to display actual video player.

        Arguments:
            _request (webob.Request): Request to handle. Imposed by `XBlock.handler`.
            _suffix (string): Slug used for routing. Imposed by `XBlock.handler`.
        Returns:
            Rendered html string as a Response (webob.Response).
        """
        player = self.get_player()
        save_state_url = self.runtime.handler_url(self, 'save_player_state')
        transcripts = render_resource(
            'static/html/transcripts.html',
            transcripts=self.route_transcripts()
        ).strip()
        return player.get_player_html(
            url=self.href, account_id=self.account_id, player_id=self.player_id,
            video_id=player.media_id(self.href),
            video_player_id='video_player_{}'.format(self.block_id),
            save_state_url=save_state_url,
            player_state=self.player_state,
            start_time=int(self.start_time.total_seconds()),  # pylint: disable=no-member
            end_time=int(self.end_time.total_seconds()),  # pylint: disable=no-member
            brightcove_js_url=VideoXBlock.get_brightcove_js_url(self.account_id, self.player_id),
            transcripts=transcripts,
        )

    @XBlock.json_handler
    def publish_event(self, data, _suffix=''):
        """
        Handler to publish XBlock event from frontend. Called by JavaScript of `student_view`.

        Arguments:
            data (dict): Data from frontend on the event.
            _suffix (string): Slug used for routing. Imposed by `XBlock.json_handler`.
        Returns:
            Data on result (dict).
        """
        try:
            event_type = data.pop('eventType')
        except KeyError:
            return {'result': 'error', 'message': 'Missing eventType in JSON data'}

        self.runtime.publish(self, event_type, data)
        return {'result': 'success'}

    def clean_studio_edits(self, data):
        """
        Given POST data dictionary 'data', clean the data before validating it.

        Try to detect player by submitted video url. If fails, it defaults to 'dummy-player'.
        Also, populate xblock's default values from settings.

        Arguments:
            data (dict): POST data.
        """
        data['player_name'] = self.fields['player_name'].default  # pylint: disable=unsubscriptable-object
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_name == PlayerName.DUMMY:
                continue
            if player_class.match(data['href']):
                data['player_name'] = player_name
                data = self.populate_default_values(data)
                log.debug("Submitted player[{}] with data: {}".format(player_name, data))
                break

    def get_player(self):
        """
        Helper method to load video player by entry-point label.

        Returns:
            Current player object (instance of a platform-specific player class).
        """
        player = BaseVideoPlayer.load_class(self.player_name)
        return player(self)

    def _get_field_help(self, field_name, field):
        """
        Get help text for field.

        First try to load override from video backend, then check field definition
        and lastly fall back to empty string.
        """
        backend_fields_help = self.get_player().fields_help
        if field_name in backend_fields_help:
            return backend_fields_help[field_name]
        elif field.help:
            return field.help
        return ''

    def initialize_studio_field_info(self, field_name, field, field_type=None):
        """
        Initialize studio editor's field info.

        Arguments:
            field_name (str): Name of a video XBlock field whose info is to be made.
            field (xblock.fields): Video XBlock field object.
            field_type (str): Type of field.
        Returns:
            info (dict): Information on a field.
        """
        info = super(VideoXBlock, self)._make_field_info(field_name, field)
        info['help'] = self._get_field_help(field_name, field)
        if field_type:
            info['type'] = field_type
        if field_name == 'handout':
            info['file_name'] = self.get_file_name_from_path(self.handout)
            info['value'] = self.get_path_for(self.handout)
        return info

    def _make_field_info(self, field_name, field):
        """
        Override and extend data of built-in method.

        Create the information that the template needs to render a form field for this field.
        Reference:
            https://github.com/edx/xblock-utils/blob/v1.0.3/xblockutils/studio_editable.py#L96

        Arguments:
            field_name (str): Name of a video XBlock field whose info is to be made.
            field (xblock.fields): Video XBlock field object.
        Returns:
            info (dict): Information on a field to be rendered in the studio editor modal.
        """
        if field_name in ('start_time', 'end_time'):
            # RelativeTime field isn't supported by default.
            info = {
                'name': field_name,
                'display_name': field.display_name if field.display_name else "",
                'is_set': field.is_set_on(self),
                'default': field.default,
                'value': field.read_from(self),
                'has_values': False,
                'allow_reset': field.runtime_options.get('resettable_editor', True),
                'list_values': None,
                'has_list_values': False,
                'type': 'string',
            }
        elif field_name in ('handout', 'transcripts', 'default_transcripts', 'token'):
            info = self.initialize_studio_field_info(field_name, field, field_type=field_name)
        else:
            info = self.initialize_studio_field_info(field_name, field)
        return info

    def prepare_studio_editor_fields(self, fields):
        """
        Order xblock fields in studio editor modal.

        Arguments:
            fields (tuple): Names of Xblock fields.
        Returns:
            made_fields (list): XBlock fields prepared to be rendered in a studio edit modal.
        """
        made_fields = [
            self._make_field_info(key, self.fields[key]) for key in fields  # pylint: disable=unsubscriptable-object
        ]
        return made_fields

    def get_file_name_from_path(self, field):
        """
        Helper for getting filename from string with path to MongoDB storage.

        Example of string:
            asset-v1-RaccoonGang+1+2018+type@asset+block@<filename>

        Arguments:
            field (str): The path to file.
        Returns:
            The name of file with an extension.
        """
        return field.split('@')[-1]

    def get_path_for(self, file_field):
        """
        Return downloaded asset url with slash in start of it.

        Url, retrieved after storing of the file field in MongoDB, looks like this:
            'asset-v1-RaccoonGang+1+2018+type@asset+block@<filename>'

        Arguments:
            file_field (str): name a file is stored in MongoDB under.
        Returns:
            Full path of a downloaded asset.
        """
        if file_field:
            return os.path.join('/', file_field)
        return ''

    @XBlock.json_handler
    def dispatch(self, request, suffix):
        """
        Dispatch request to XBlock's player.

        Arguments:
            request (xblock.django.request.DjangoWebobRequest): Incoming request data.
            suffix (str): Slug used for routing. Imposed by `XBlock.json_handler`.
        Returns:
             Depending on player's `dispatch()` entry point, either info on video / Brightcove account or None value
             (when performing some action via Brightcove API) may be returned.
        """
        return self.get_player().dispatch(request, suffix)

    @XBlock.handler
    def ui_dispatch(self, _request, suffix):
        """
        Dispatcher for a requests sent by dynamic Front-end components.

        Typical use case: Front-end wants to check with backend if it's ok to show certain part of UI.

        Arguments:
            _request (xblock.django.request.DjangoWebobRequest): Incoming request data. Not used.
            suffix (str): Slug used for routing.
        Returns:
             Response object, containing response data.
        """
        resp = {
            'success': True,
            'data': {}
        }
        if suffix == 'get-metadata':
            resp['data'] = {'metadata': self.metadata}
        elif suffix == 'can-show-backend-settings':
            player = self.get_player()
            if str(self.player_name) == PlayerName.BRIGHTCOVE:
                resp['data'] = player.can_show_settings()
            else:
                resp['data'] = {'canShow': False}

        response = Response(json.dumps(resp), content_type='application/json')
        return response

    def authenticate_video_api(self, token):
        """
        Authenticate to a video platform's API.

        Arguments:
            token (str): token provided by a user before the save button was clicked (for handlers).
        Returns:
            error_message (dict): Status message for template rendering.
            auth_data (dict): Tokens and credentials, necessary to perform authorised API requests.
        """
        # TODO move auth fields validation and kwargs population to specific backends
        # Handles a case where no token was provided by a user
        kwargs = {'token': token}

        # Handles a case where no account_id was provided by a user
        if str(self.player_name) == PlayerName.BRIGHTCOVE:
            if self.account_id == self.fields['account_id'].default:  # pylint: disable=unsubscriptable-object
                error_message = 'In order to authenticate to a video platform\'s API, please provide an Account Id.'
                return {}, error_message
            kwargs['account_id'] = self.account_id

        player = self.get_player()
        if str(self.player_name) == PlayerName.BRIGHTCOVE and self.metadata.get('client_id'):
            auth_data = {
                'client_secret': self.metadata.get('client_secret'),
                'client_id': self.metadata.get('client_id'),
            }
            error_message = ''
        else:
            auth_data, error_message = player.authenticate_api(**kwargs)

        # Metadata is to be updated on each authentication effort.
        self.update_metadata_authentication(auth_data=auth_data, player=player)
        return auth_data, error_message

    @XBlock.json_handler
    def authenticate_video_api_handler(self, data, _suffix=''):
        """
        Xblock handler to authenticate to a video platform's API. Called by JavaScript of `studio_view`.

        Arguments:
            data (dict): Data from frontend, necessary for authentication (tokens, account id, etc).
            _suffix (str): Slug used for routing. Imposed by `XBlock.json_handler`.
        Returns:
            response (dict): Status messages key-value pairs.
        """
        # Fetch a token provided by a user before the save button was clicked.
        token = str(data)

        is_default_token = token == self.fields['token'].default  # pylint: disable=unsubscriptable-object
        is_youtube_player = str(self.player_name) != PlayerName.YOUTUBE  # pylint: disable=unsubscriptable-object
        if not token or (is_default_token and is_youtube_player):
            return {
                'error_message': "In order to authenticate to a video platform's API, "
                                 "please provide a Video API Token."
                }

        _auth_data, error_message = self.authenticate_video_api(token)
        if error_message:
            return {'error_message': error_message}
        return {'success_message': 'Successfully authenticated to the video platform.'}

    def update_metadata_authentication(self, auth_data, player):
        """
        Update video xblock's metadata field with video platform's API authentication data.

        Arguments:
            auth_data (dict): Data containing credentials necessary for authentication.
            player (object): Object of a platform-specific player class.
        """
        # In case of successful authentication:
        for key in auth_data:
            if key not in player.metadata_fields:
                # Only backend-specific parameters are to be stored
                continue
            self.metadata[key] = auth_data[key]
        # If the last authentication effort was not successful, metadata should be updated as well.
        # Since video xblock metadata may store various information, this is to update the auth data only.
        if not auth_data:
            self.metadata['token'] = ''  # Wistia API
            self.metadata['access_token'] = ''  # Brightcove API
            self.metadata['client_id'] = ''  # Brightcove API
            self.metadata['client_secret'] = ''  # Brightcove API

    @XBlock.json_handler
    def upload_default_transcript_handler(self, data, _suffix=''):
        """
        Upload a transcript, fetched from a video platform's API, to video xblock.

        Arguments:
            data (dict): Data from frontend on a default transcript to be fetched from a video platform.
            _suffix (str): Slug used for routing. Imposed by `XBlock.json_handler`.
        Returns:
            response (dict): Data on a default transcript, fetched from a video platform.

        """
        log.debug("Uploading default transcript with data: {}".format(data))
        player = self.get_player()
        video_id = player.media_id(self.href)
        lang_code = str(data.get(u'lang'))
        lang_label = str(data.get(u'label'))
        source = str(data.get(u'source', ''))
        sub_url = str(data.get(u'url'))

        reference_name = create_reference_name(lang_label, video_id, source)

        # Fetch text of single default transcript:
        unicode_subs_text = player.download_default_transcript(sub_url, lang_code)
        if not unicode_subs_text:
            return {'failure_message': _("Couldn't upload transcript text.")}

        if not player.default_transcripts_in_vtt:
            prepared_subs = self.convert_caps_to_vtt(caps=unicode_subs_text)
        else:
            prepared_subs = unicode_subs_text

        file_name, external_url = self.create_transcript_file(
            trans_str=prepared_subs, reference_name=reference_name
        )

        # Exceptions are handled on the frontend
        success_message = 'Successfully uploaded "{}".'.format(file_name)
        response = {
            'success_message': success_message,
            'lang': lang_code,
            'url': external_url,
            'label': lang_label,
            'source': source,
        }
        log.debug("Uploaded default transcript: {}".format(response))
        return response

    def get_enabled_transcripts(self):
        """
        Get transcripts from different sources depending on current usage mode.
        """
        if self.threeplaymedia_streaming:
            transcripts = list(self.fetch_available_3pm_transcripts())
        else:
            try:
                transcripts = json.loads(self.transcripts) if self.transcripts else []
                assert isinstance(transcripts, list)
            except (ValueError, AssertionError):
                log.exception("JSON parser can't handle 'self.transcripts' field value: {}".format(self.transcripts))
                return []
        return normalize_transcripts(transcripts)
