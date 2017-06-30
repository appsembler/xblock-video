"""
Base Video Xblock mocks.
"""
import json
from copy import deepcopy
from collections import OrderedDict
from mock import Mock
import requests


from video_xblock.exceptions import VideoXBlockMockException


class ResponseStub(object):
    """
    Dummy ResponseStub class.
    """

    def __init__(self, **kwargs):
        """
        Delegate kwargs to class properties.
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def text(self):
        """
        Make response compatible with requests.Response.
        """
        return getattr(self, 'body', '')

    @property
    def content(self):
        """
        Make response compatible with requests.Response.
        """
        return getattr(self, 'body', '')

    def get(self, key):
        """
        Allow to fetch data from response body by key.
        """
        body = getattr(self, 'body', '')
        if body:
            try:
                return json.loads(body)[key]
            except KeyError:
                pass

    def json(self):
        """
        Make response compatible with requests.Response.
        """
        return getattr(self, 'body', '')


class BaseMock(Mock):
    """
    Base custom mock class.
    """

    # `outcomes` should be in the format of dict().items() to keep the order of items.
    # First argument: result name, second argument - dictionary containing result data.
    # Example: (("key1", {}), ("key2", {}), ...)
    outcomes = ()
    to_return = []

    def __init__(self, **kwargs):
        """
        Set specific properties from the kwargs.
        """
        super(BaseMock, self).__init__()
        if 'mock_magic' in kwargs:
            self.mock = kwargs['mock_magic']
        self.xblock = kwargs.get('xblock')
        event = kwargs.get('event')
        if not event:
            raise VideoXBlockMockException(
                "%s: `event` parameter is not provided or not in %s." % (
                    self.__class__.__name__, self.ordered_results.keys()
                )
            )
        if event and event in self.get_outcomes():
            self.event = event

    @property
    def ordered_results(self):
        """
        Transform `outcomes` to dict.
        """
        return OrderedDict(self.outcomes)

    @property
    def expected_value(self):
        """
        Should return expected value after mock is applied.
        """
        ret = []
        if self.event in self.ordered_results:
            for item in self.to_return:
                ret.append(self.ordered_results[self.event][item])
        return tuple(ret)

    @classmethod
    def get_outcomes(cls):
        """
        Return available events. Ensures that outcomes have correct data format.
        """
        for key, val in cls.outcomes:
            if isinstance(key, str) and isinstance(val, dict) and key:
                yield key
            else:
                raise VideoXBlockMockException(
                    "%s.outcomes have invalid data format: container=%s, item=%s" % (
                        cls.__name__, type(cls.outcomes), type(cls.outcomes[0])
                    )
                )

    def apply_mock(self, mocked_objects):  # pylint: disable=unused-argument
        """
        Save state of object before mocks are applied.
        """
        mocked_objects.append({
            'obj': requests,
            'attrs': ['get', ],
            'value': [deepcopy(requests.get), ]
        })
        return mocked_objects


class MockCourse(object):
    """
    Mock Course object with required parameters.
    """

    def __init__(self, course_id):
        """
        Delegate course_id to class property and set course's language.
        """
        self.course_id = course_id
        self.language = 'en'


class RequestsMock(BaseMock):
    """
    Base class for mocking `requests.get`.
    """

    def get(self):
        """
        Mock method that substitutes `requests.get` one.
        """
        raise NotImplementedError

    def apply_mock(self, mocked_objects):
        """
        Save state of auth related entities before mocks are applied.
        """
        super(RequestsMock, self).apply_mock(mocked_objects)
        requests.get = self.get()
        return mocked_objects
