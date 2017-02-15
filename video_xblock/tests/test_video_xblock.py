"""
Test cases for video_xblock.
"""

import datetime
import json
import unittest

import mock

from django.test import RequestFactory
from django.conf import settings
from xblock.field_data import DictFieldData
from xblock.test.tools import TestRuntime

from video_xblock import VideoXBlock
from video_xblock.utils import ugettext as _

settings.configure()


class VideoXBlockTests(unittest.TestCase):
    """
    Test cases for video_xblock.
    """

    def setUp(self):
        """
        Create a XBlock VideoXBlock for testing purpose.
        """
        result = super(VideoXBlockTests, self).setUp()
        runtime = TestRuntime()  # pylint: disable=abstract-class-instantiated
        self.block = VideoXBlock(runtime, DictFieldData({
            'account_id': 'account_id',
        }), mock.Mock())
        return result

    def test_fields_xblock(self):
        """
        Test xblock fields consistency with their default values.
        """
        self.assertEqual(self.block.display_name, _('Video'))
        self.assertEqual(self.block.href, '')
        self.assertEqual(self.block.account_id, 'account_id')
        self.assertEqual(self.block.player_id, 'default')
        self.assertEqual(self.block.player_name, 'dummy-player')
        self.assertEqual(self.block.start_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.block.end_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.block.current_time, 0)
        self.assertEqual(self.block.playback_rate, 1)
        self.assertEqual(self.block.volume, 1)
        self.assertEqual(self.block.muted, False)
        self.assertEqual(self.block.captions_language, '')
        self.assertEqual(self.block.transcripts_enabled, False)
        self.assertEqual(self.block.captions_enabled, False)
        self.assertEqual(self.block.handout, '')
        self.assertEqual(self.block.transcripts, '')
        self.assertEqual(self.block.download_transcript_allowed, False)

    def test_player_state(self):
        """
        Test player state property.
        """
        self.block.course_id = 'test:course:id'
        self.block.runtime.modulestore = mock.Mock(get_course=MockCourse)
        self.assertDictEqual(
            self.block.player_state,
            {
                'current_time': self.block.current_time,
                'muted': self.block.muted,
                'playback_rate': self.block.playback_rate,
                'volume': self.block.volume,
                'transcripts': [],
                'transcripts_enabled': self.block.transcripts_enabled,
                'captions_enabled': self.block.captions_enabled,
                'captions_language': 'en',
                'transcripts_object': {}
            }
        )

    def test_get_brightcove_js_url(self):
        """
        Test brightcove.js url generation.
        """
        self.assertEqual(
            VideoXBlock.get_brightcove_js_url(self.block.account_id, self.block.player_id),
            "https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
                account_id=self.block.account_id,
                player_id=self.block.player_id
            )
        )

    def test_save_player_state(self):
        """
        Test player state saving.
        """
        self.block.course_id = 'test:course:id'
        self.block.runtime.modulestore = mock.Mock(get_course=MockCourse)
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
        response = self.block.save_player_state(request)
        self.assertEqual('{"success": true}', response.body)  # pylint: disable=no-member
        self.assertDictEqual(self.block.player_state, {
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


class MockCourse(object):
    """
    Mock Course object with required parameters.
    """

    def __init__(self, course_id):
        """
        Initialize mock course object.
        """
        self.course_id = course_id
        self.language = 'en'
