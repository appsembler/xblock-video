"""
Brightcove backend mocks.
"""
import json
from copy import copy, deepcopy

from video_xblock.exceptions import VideoXBlockException, VideoXBlockMockException
from video_xblock.tests.mocks.base import BaseMock, RequestsMock, ResponseStub
from video_xblock.backends import brightcove


class BrightcoveAuthMock(BaseMock):
    """
    Brightcove auth mock class.
    """

    outcomes = (
        (
            'credentials_created',
            {
                'client_secret': 'brightcove_client_secret',
                'client_id': 'brightcove_client_id',
                'error_message': ''
            }
        ),
        (
            'auth_failed',
            {
                'client_secret': '',
                'client_id': '',
                'error_message': 'Authentication to Brightcove API failed: no client credentials have been retrieved.'
            }
        )
    )

    def create_credentials(self):
        """
        Mock `get_client_credentials` returned value.
        """
        if self.event == 'auth_failed':
            self.side_effect = VideoXBlockException(self.ordered_results[self.event]['error_message'])
        self.return_value = (
            self.ordered_results[self.event]['client_secret'],
            self.ordered_results[self.event]['client_id'],
            self.ordered_results[self.event]['error_message']
        )
        return self

    @property
    def expected_value(self):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        ret = copy(self.ordered_results[self.event])
        error = ret.pop('error_message')
        return ret, error

    def apply_mock(self, mocked_objects):
        """
        Save state of auth related entities before mocks are applied.
        """
        mocked_objects.append({
            'obj': brightcove.BrightcoveApiClient,
            'attrs': ['create_credentials', ],
            'value': [brightcove.BrightcoveApiClient.create_credentials, ]
        })
        brightcove.BrightcoveApiClient.create_credentials = self.create_credentials()
        return mocked_objects


class BrightcoveDefaultTranscriptsMock(BaseMock):
    """
    Brightcove default transcripts mock class.
    """

    _default_transcripts = [
        {'label': u'English', 'lang': u'en', 'url': None},
        {'label': u'Ukrainian', 'lang': u'uk', 'url': None}
    ]

    _response = {
        "master": {
            "url": "http://host/master.mp4"
        },
        "poster": {
            "url": "http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-poster.png",
            "width": 640,
            "height": 360
        },
        "thumbnail": {
            "url": "http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-thumbnail.png",
            "width": 160,
            "height": 90
        },
        "capture-images": False,
        "callbacks": ["http://solutions.brightcove.com/bcls/di-api/di-callbacks.php"]
    }

    transcripts = [
        {
            "url": "http://learning-services-media.brightcove.com/captions/for_video/Water-in-Motion.vtt",
            "srclang": "en",
            "kind": "captions",
            "label": "EN",
            "default": True
        },
        {
            "url": "http://learning-services-media.brightcove.com/captions/for_video/Water-in-Motion.vtt",
            "srclang": "uk",
            "kind": "captions",
            "label": "UK",
            "default": False
        }
    ]

    outcomes = (
        (
            'no_credentials',
            {
                'default_transcripts': [],
                'message': 'No API credentials provided'
            }
        ),
        (
            'fetch_transcripts_exception',
            {
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'no_captions_data',
            {
                'default_transcripts': [],
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'success',
            {
                'default_transcripts': _default_transcripts,
                'message': ''
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def api_client_get(self):
        """
        Mock for `api_client` method.
        """
        if self.event == 'fetch_transcripts_exception':
            self.side_effect = self.mock()
        elif self.event == 'no_captions_data':
            self.return_value = ResponseStub(status_code=200, body=json.dumps(self._response))
        else:
            ret = copy(self._response)
            ret['text_tracks'] = self.transcripts
            self.return_value = ResponseStub(status_code=200, body=json.dumps(ret))
        return self

    def no_credentials(self):
        """
        Return xblock metadata.
        """
        if self.event == 'no_credentials':
            return {'client_id': '', 'client_secret': ''}
        else:
            return self.mock

    # @XBlock.register_temp_plugin(brightcove.BrightcovePlayer, 'wistia')
    def apply_mock(self, mocked_objects):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        if not self.xblock:
            raise VideoXBlockMockException("`xblock` parameter is required for %s." % self.__class__)
        mocked_objects.append({
            'obj': brightcove.BrightcoveApiClient,
            'attrs': ['get', ],
            'value': [deepcopy(brightcove.BrightcoveApiClient.get), ]
        })
        mocked_objects.append({
            'obj': self.xblock,
            'attrs': ['metadata', ],
            'value': [deepcopy(self.xblock.metadata), ]
        })
        brightcove.BrightcoveApiClient.get = BrightcoveDefaultTranscriptsMock(
            mock_magic=brightcove.BrightcoveApiClientError, event=self.event
        ).api_client_get()
        self.xblock.metadata = self.no_credentials()
        return mocked_objects


class BrightcoveDownloadTranscriptMock(RequestsMock):
    """
    Brightcove download default transcript mock class.
    """

    _vtt = """WEBVTT

00:06.047 --> 00:06.068
Hi.

00:06.070 --> 00:08.041
I'm Bob Bailey, a Learning Specialist with Brightcove.

00:09.041 --> 00:11.003
In this video, we'll learn about Brightcove Smart Players

00:21.052 --> 00:23.027
the next few years.

00:25.042 --> 00:27.094
accessed from mobile devices."""

    outcomes = (
        ('wrong_arguments', {'transcript': [], 'message': '`url` parameter is required.'}),
        ('success', {'transcript': _vtt, 'message': ''})
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        self.return_value = ResponseStub(status_code=200, body=self._vtt)
        return lambda x: self.return_value
