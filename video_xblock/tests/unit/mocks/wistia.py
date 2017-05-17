"""
Wistia backend mocks.
"""
import json
from copy import copy, deepcopy
import requests

from xblock.core import XBlock

from video_xblock.backends import wistia
from video_xblock.tests.unit.mocks.base import BaseMock, RequestsMock, ResponseStub


class WistiaAuthMock(RequestsMock):
    """
    Wistia auth mock class.
    """

    return_value = ResponseStub(status_code=200, body='')

    outcomes = (
        (
            'not_authorized',
            {'auth_data': {'token': 'some_token'}, 'error_message': 'Authentication failed.'}
        ),
        (
            'success',
            {'auth_data': {'token': 'some_token'}, 'error_message': ''}
        )
    )

    to_return = ['auth_data', 'error_message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'not_authorized':
            self.return_value = ResponseStub(status_code=401)
        return lambda x: self.return_value


class WistiaDefaultTranscriptsMock(BaseMock):
    """
    Wistia default transcripts mock class.
    """

    _expected = [
        {
            'lang': u'en',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here',
            'label': u'English'
        },
        {
            'lang': u'uk',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here',
            'label': u'Ukrainian'
        }
    ]

    _default_transcripts = [
        {'english_name': u'English', 'language': u'eng',
         'text': 'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here'},
        {'english_name': u'Ukrainian', 'language': u'ukr',
         'text': 'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here'}
    ]

    outcomes = (
        (
            'request_data_exception',
            {
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'success_and_data_lang_code',
            {
                'default_transcripts': _expected,
                'message': ''
            }
        ),
        (
            'success_and_data_lang_code_exception',
            {
                'default_transcripts': _default_transcripts,
                'message': 'LanguageReverseError'
            }
        ),
        (
            'success_no_data',
            {
                'default_transcripts': [],
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'success_invalid_json',
            {
                'default_transcripts': [],
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'returned_not_found',
            {
                'default_transcripts': [],
                'message': 'doesn\'t exist.'
            }
        ),
        (
            'invalid_request',
            {
                'default_transcripts': [],
                'message': 'Invalid request.'
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'request_data_exception':
            self.side_effect = self.mock()
            return self
        else:
            default_transcripts = copy(self._default_transcripts)
            default_transcripts[0]['language'] = 'en'
            return_value_by_event = {
                'success_and_data_lang_code_exception': {
                    'status_code': 200,
                    'body': json.dumps(default_transcripts)
                },
                'success_and_data_lang_code': {
                    'status_code': 200,
                    'body': json.dumps(self._default_transcripts)
                },
                'success_no_data': {
                    'status_code': 200,
                    'body': '{}'
                },
                'success_invalid_json': {
                    'status_code': 200,
                    'body': '{{invalid_json'
                },
                'returned_not_found': {
                    'status_code': 404,
                    'body': '{}'
                },
                'invalid_request': {
                    'status_code': 400,
                    'body': 'Invalid request.'
                }
            }
            self.return_value = ResponseStub(**return_value_by_event[self.event])
        return lambda x: self.return_value

    def apply_mock(self, mocked_objects):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        super(WistiaDefaultTranscriptsMock, self).apply_mock(mocked_objects)
        requests.get = WistiaDefaultTranscriptsMock(
            mock_magic=requests.exceptions.RequestException, event=self.event
        ).get()
        return mocked_objects


class WistiaDownloadTranscriptMock(BaseMock):
    """
    Wistia download default transcript mock class.
    """

    _default_transcripts = [
        {
            'lang': u'en',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here',
            'label': u'English'
        },
        {
            'lang': u'uk',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here',
            'label': u'Ukrainian'
        }
    ]

    outcomes = (
        (
            'wrong_arguments',
            {
                'transcript': [],
                'message': '`language_code` parameter is required.'
            }
        ),
        (
            'success_en',
            {
                'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=en&name=&v=set_video_id_here ',
                'message': ''
            }
        ),
        (
            'success_uk',
            {
                'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here ',
                'message': ''
            }
        )
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute player method.
        """
        self.return_value = self._default_transcripts
        return self

    def __iter__(self):
        """
        Iter through default transcripts.
        """
        return iter(self._default_transcripts)

    @XBlock.register_temp_plugin(wistia.WistiaPlayer, 'wistia')
    def apply_mock(self, mocked_objects):
        """
        Save state of download transcript related entities before mocks are applied.
        """
        player = XBlock.load_class('wistia')
        mocked_objects.append({
            'obj': player,
            'attrs': ['default_transcripts', ],
            'value': [deepcopy(player.default_transcripts), ]
        })
        player.default_transcripts = self.get()
        return mocked_objects
