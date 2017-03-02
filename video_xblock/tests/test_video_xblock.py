"""
Test cases for video_xblock.
"""

import datetime
import json
import mock

from django.test import RequestFactory
from django.conf import settings

from video_xblock import VideoXBlock
from video_xblock.utils import ugettext as _
from video_xblock.tests.base import VideoXBlockTestBase
from video_xblock.tests.mocks import MockCourse
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

    def test_player_state(self):
        """
        Test player state property.
        """
        self.xblock.course_id = 'test:course:id'
        self.xblock.runtime.modulestore = mock.Mock(get_course=MockCourse)
        self.assertDictEqual(
            self.xblock.player_state,
            {
                'current_time': self.xblock.current_time,
                'muted': self.xblock.muted,
                'playback_rate': self.xblock.playback_rate,
                'volume': self.xblock.volume,
                'transcripts': [],
                'transcripts_enabled': self.xblock.transcripts_enabled,
                'captions_enabled': self.xblock.captions_enabled,
                'captions_language': 'en',
                'transcripts_object': {}
            }
        )

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

    def test_save_player_state(self):
        """
        Test player state saving.
        """
        self.xblock.course_id = 'test:course:id'
        self.xblock.runtime.modulestore = mock.Mock(get_course=MockCourse)
        data = {
            'currentTime': 5,
            'muted': True,
            'playbackRate': 2,
            'volume': 0.5,
            'transcripts': [],
            'transcriptsEnabled': True,
            'captionsEnabled': True,
            'captionsLanguage': 'ru',
            'transcripts_object': {}
        }
        factory = RequestFactory()
        request = factory.post('', json.dumps(data), content_type='application/json')
        response = self.xblock.save_player_state(request)
        self.assertEqual('{"success": true}', response.body)  # pylint: disable=no-member
        self.assertDictEqual(self.xblock.player_state, {
            'current_time': data['currentTime'],
            'muted': data['muted'],
            'playback_rate': data['playbackRate'],
            'volume': data['volume'],
            'transcripts': data['transcripts'],
            'transcripts_enabled': data['transcriptsEnabled'],
            'captions_enabled': data['captionsEnabled'],
            'captions_language': data['captionsLanguage'],
            'transcripts_object': {}
        })
