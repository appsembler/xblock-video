"""
Test cases for video_xblock.
"""

import datetime
from mock import patch, Mock, PropertyMock

from django.conf import settings
from xblock.fragment import Fragment

from video_xblock import VideoXBlock
from video_xblock.utils import ugettext as _
from video_xblock.tests.unit.base import VideoXBlockTestBase

from video_xblock.constants import PlayerName


settings.configure()


class VideoXBlockTests(VideoXBlockTestBase):
    """
    Test cases for video_xblock.
    """

    def test_fields_xblock(self):
        """
        Test xblock fields consistency with their default values.
        """

        self.assertEqual(self.xblock.display_name, _('Video'))
        self.assertEqual(self.xblock.href, '')
        self.assertEqual(self.xblock.account_id, 'account_id')
        self.assertEqual(self.xblock.player_id, 'default')
        self.assertEqual(self.xblock.player_name, PlayerName.DUMMY)
        self.assertEqual(self.xblock.start_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.end_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.current_time, 0)
        self.assertEqual(self.xblock.playback_rate, 1)
        self.assertEqual(self.xblock.volume, 1)
        self.assertEqual(self.xblock.muted, False)
        self.assertEqual(self.xblock.captions_language, '')
        self.assertEqual(self.xblock.transcripts_enabled, False)
        self.assertEqual(self.xblock.captions_enabled, False)
        self.assertEqual(self.xblock.handout, '')
        self.assertEqual(self.xblock.transcripts, '')
        self.assertEqual(self.xblock.download_transcript_allowed, False)
        self.assertEqual(self.xblock.download_video_allowed, False)
        self.assertEqual(self.xblock.download_video_url, '')

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

        # Act
        studio_view = self.xblock.student_view(unused_context_stub)

        # Assert
        self.assertIsInstance(studio_view, Fragment)
        render_resource_mock.assert_called_once_with(
            'static/html/student_view.html',
            display_name='Video',
            download_transcript_allowed=False,
            download_video_url=False,
            handout='',
            handout_file_name='',
            player_url='/player/url',
            transcript_download_link='/transcript/download/url'+'/transcript/link.vtt',
            transcripts='transcripts.vtt',
            usage_id='deprecated_string'
        )
        resource_string_mock.assert_called_with('static/css/student-view.css')
        handler_url.assert_called_with(self.xblock, 'download_transcript')
        route_transcripts.assert_called_once_with(self.xblock.transcripts)
