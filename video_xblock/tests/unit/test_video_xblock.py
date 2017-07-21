"""
Test cases for video_xblock.
"""

import datetime
import json

from mock import patch, Mock, MagicMock, PropertyMock

from web_fragments.fragment import FragmentResource
from xblock.fragment import Fragment

from video_xblock import VideoXBlock, __version__
from video_xblock.constants import PlayerName
from video_xblock.utils import ugettext as _
from video_xblock.tests.unit.base import VideoXBlockTestBase


class VideoXBlockTests(VideoXBlockTestBase):
    """
    Test cases for video_xblock.
    """

    def test_xblock_fields_default_values(self):
        """
        Test xblock fields consistency with their default values.
        """

        self.assertEqual(self.xblock.account_id, 'account_id')
        self.assertEqual(self.xblock.captions_enabled, False)
        self.assertEqual(self.xblock.captions_language, '')
        self.assertEqual(self.xblock.current_time, 0)
        self.assertEqual(self.xblock.default_transcripts, '')
        self.assertEqual(self.xblock.display_name, _('Video'))
        self.assertEqual(self.xblock.download_transcript_allowed, False)
        self.assertEqual(self.xblock.download_video_allowed, False)
        self.assertEqual(self.xblock.download_video_url, '')
        self.assertEqual(self.xblock.end_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.handout, '')
        self.assertEqual(self.xblock.href, '')
        self.assertEqual(self.xblock.muted, False)
        self.assertEqual(self.xblock.playback_rate, 1)
        self.assertEqual(self.xblock.player_id, 'default')
        self.assertEqual(self.xblock.player_name, PlayerName.DUMMY)
        self.assertEqual(self.xblock.start_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.threeplaymedia_apikey, '')
        self.assertEqual(self.xblock.threeplaymedia_file_id, '')
        self.assertEqual(self.xblock.token, '')
        self.assertEqual(self.xblock.transcripts, '')
        self.assertEqual(self.xblock.transcripts_enabled, False)
        self.assertEqual(self.xblock.volume, 1)

    def test_get_brightcove_js_url(self):
        """
        Test brightcove.js url generation.
        """
        self.assertEqual(
            VideoXBlock.get_brightcove_js_url(self.xblock.account_id, self.xblock.player_id),
            "https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
                account_id=self.xblock.account_id,
                player_id=self.xblock.player_id
            )
        )

    @patch('video_xblock.video_xblock.render_resource')
    @patch.object(VideoXBlock, 'route_transcripts')
    @patch.object(VideoXBlock, 'get_player')
    @patch.object(VideoXBlock, 'player_state', new_callable=PropertyMock)
    @patch.object(VideoXBlock, 'get_brightcove_js_url')
    def test_render_player(
            self, brightcove_js_url_mock, player_state_mock, player_mock,
            route_transcripts_mock, render_resource_mock
    ):
        # Arrange
        request_mock, suffix_mock = Mock(), Mock()
        render_resource_mock.return_value = u'vtt transcripts'
        handler_url = self.xblock.runtime.handler_url = Mock()
        get_player_html_mock = player_mock.return_value.get_player_html
        media_id_mock = player_mock.return_value.media_id

        # Act
        rendered_player = self.xblock.render_player(request_mock, suffix_mock)

        # Assert
        self.assertEqual(rendered_player, get_player_html_mock.return_value)
        get_player_html_mock.assert_called_once_with(
            account_id=self.xblock.account_id,
            brightcove_js_url=brightcove_js_url_mock.return_value,
            end_time=self.xblock.end_time.total_seconds(),  # pylint: disable=no-member
            player_id=self.xblock.player_id,
            player_state=player_state_mock.return_value,
            save_state_url=handler_url.return_value,
            start_time=self.xblock.start_time.total_seconds(),  # pylint: disable=no-member
            transcripts=u'vtt transcripts',
            url=self.xblock.href,
            video_id=media_id_mock.return_value,
            video_player_id='video_player_block_id'
        )
        brightcove_js_url_mock.assert_called_once_with(
            self.xblock.account_id, self.xblock.player_id
        )
        player_state_mock.assert_called_once_with()
        render_resource_mock.assert_called_once_with(
            'static/html/transcripts.html',
            transcripts=route_transcripts_mock()
        )
        player_mock.assert_called_once_with()
        handler_url.assert_called_once_with(self.xblock, 'save_player_state')
        request_mock.assert_not_called()
        suffix_mock.assert_not_called()

    @patch('video_xblock.video_xblock.render_resource')
    @patch('video_xblock.video_xblock.resource_string')
    @patch.object(VideoXBlock, 'route_transcripts')
    def test_student_view(self, route_transcripts, resource_string_mock, render_resource_mock):
        # Arrange
        unused_context_stub = object()
        render_resource_mock.return_value = u'<iframe/>'
        handler_url = self.xblock.runtime.handler_url = Mock()
        handler_url.side_effect = ['/player/url', '/transcript/download/url']
        route_transcripts.return_value = 'transcripts.vtt'
        self.xblock.get_transcript_download_link = Mock(return_value='/transcript/link.vtt')
        self.xblock.threeplaymedia_streaming = True

        # Act
        student_view = self.xblock.student_view(unused_context_stub)

        # Assert
        self.assertIsInstance(student_view, Fragment)
        render_resource_mock.assert_called_once_with(
            'static/html/student_view.html',
            display_name='Video',
            download_transcript_allowed=False,
            transcripts_streaming_enabled=True,
            download_video_url=False,
            handout='',
            handout_file_name='',
            player_url='/player/url',
            transcript_download_link='/transcript/download/url'+'/transcript/link.vtt',
            transcripts='transcripts.vtt',
            usage_id='usage_id',
            version=__version__,
        )
        resource_string_mock.assert_called_with('static/css/student-view.css')
        handler_url.assert_called_with(self.xblock, 'download_transcript')
        route_transcripts.assert_called_once_with()

    @patch('video_xblock.video_xblock.ALL_LANGUAGES', new_callable=MagicMock)
    @patch('video_xblock.video_xblock.render_template')
    @patch.object(VideoXBlock, 'route_transcripts')
    @patch.object(VideoXBlock, 'authenticate_video_api')
    @patch.object(VideoXBlock, '_update_default_transcripts')
    @patch.object(VideoXBlock, 'prepare_studio_editor_fields')
    @patch('video_xblock.video_xblock.resource_string')
    def test_studio_view_uses_correct_context(
            self, resource_string_mock, prepare_fields_mock, update_default_transcripts_mock,
            authenticate_video_api_mock, _route_transcripts, render_template_mock,
            all_languages_mock
    ):
        # Arrange
        unused_context_stub = object()
        all_languages_mock.__iter__.return_value = [['en', 'English']]
        self.xblock.runtime.handler_url = handler_url_mock = Mock()
        update_default_transcripts_mock.return_value = (
            ['stub1', 'stub2'], 'Stub autoupload messate'
        )
        prepare_fields_mock.side_effect = \
            basic_fields_stub, advanced_fields_stub, transcripts_fields_stub, three_pm_fields_stub = [
                [{'name': 'display_name'}],
                [{'name': 'href'}],
                [{'transcripts': 'foo'}],
                [{'threeplaymedia_file_id': '12345'}]
            ]
        resource_string_mock.side_effect = [
            'static/css/student-view.css',
            'static/css/transcripts-upload.css',
            'static/css/studio-edit.css',
            'static/css/studio-edit-accordion.css',
            'static/js/runtime-handlers.js',
            'static/js/studio-edit/utils.js',
            'static/js/studio-edit/studio-edit.js',
            'static/js/studio-edit/transcripts-autoload.js',
            'static/js/studio-edit/transcripts-manual-upload.js',
        ]

        expected_context = {
            'advanced_fields': advanced_fields_stub,
            'auth_error_message': '',
            'basic_fields': basic_fields_stub,
            'courseKey': 'course_key',
            'default_transcripts': self.xblock.default_transcripts,
            'download_transcript_handler_url': handler_url_mock.return_value,
            'enabled_default_transcripts': [],
            'initial_default_transcripts': ['stub1', 'stub2'],
            'languages': [{'code': 'en', 'label': 'English'}],
            'player_name': self.xblock.player_name,
            'players': PlayerName,
            'sources': [('DEFAULT', 'default'), ('THREE_PLAY_MEDIA', '3play-media'), ('MANUAL', 'manual')],
            'three_pm_fields': three_pm_fields_stub,
            'transcripts': [],
            'transcripts_fields': transcripts_fields_stub,
            'transcripts_autoupload_message': 'Stub autoupload messate',
            'transcripts_type': 'manual',
        }

        # Act
        self.xblock.studio_view(unused_context_stub)

        # Assert
        render_template_mock.assert_called_once_with('studio-edit.html', **expected_context)
        handler_url_mock.assert_called_with(self.xblock, 'download_transcript')
        update_default_transcripts_mock.assert_called_once()
        authenticate_video_api_mock.assert_not_called()

    @staticmethod
    def _make_fragment_resource(file_name):
        """
        Helper factory method to create `FragmentResource` used in tests.
        """
        if file_name.endswith('.js'):
            return FragmentResource('text', file_name, 'application/javascript', 'foot')
        elif file_name.endswith('.css'):
            return FragmentResource('text', file_name, 'text/css', 'head')

    @patch('video_xblock.video_xblock.render_template')
    @patch.object(VideoXBlock, 'route_transcripts')
    @patch('video_xblock.video_xblock.resource_string')
    def test_studio_view_uses_correct_resources(
            self, resource_string_mock, _route_transcripts, _render_template_mock
    ):
        # Arrange
        unused_context_stub = object()
        self.xblock.runtime.handler_url = Mock()
        resource_string_mock.side_effect = expected_resources = [
            'static/css/student-view.css',
            'static/css/transcripts-upload.css',
            'static/css/studio-edit.css',
            'static/css/studio-edit-accordion.css',
            'static/js/runtime-handlers.js',
            'static/js/studio-edit/utils.js',
            'static/js/studio-edit/studio-edit.js',
            'static/js/studio-edit/transcripts-autoload.js',
            'static/js/studio-edit/transcripts-manual-upload.js',
        ]

        expected_fragment_resources = map(
            self._make_fragment_resource, expected_resources
        )

        # Act
        studio_view = self.xblock.studio_view(unused_context_stub)

        # Assert
        self.assertIsInstance(studio_view, Fragment)
        self.assertEqual(studio_view.resources, expected_fragment_resources)

    @patch('video_xblock.video_xblock.normalize_transcripts')
    def test_get_enabled_transcripts_success(self, normalize_transcripts_mock):
        # Arrange
        normalize_transcripts_mock.side_effect = lambda x: x
        self.xblock.transcripts = test_transcripts = '[{"transcript":"json"}]'
        # Act
        transcripts = self.xblock.get_enabled_transcripts()
        # Assert
        self.assertIsInstance(transcripts, list)
        self.assertEqual(transcripts, json.loads(test_transcripts))
        normalize_transcripts_mock.assert_called_once()

    @patch('video_xblock.video_xblock.normalize_transcripts')
    def test_get_enabled_transcripts_failure(self, normalize_transcripts_mock):
        # Arrange
        normalize_transcripts_mock.side_effect = lambda x: x
        self.xblock.transcripts = '[{"transcript":bad_json}]'
        # Act
        transcripts = self.xblock.get_enabled_transcripts()
        # Assert
        self.assertIsInstance(transcripts, list)
        self.assertEqual(transcripts, [])
        self.assertFalse(normalize_transcripts_mock.called)
