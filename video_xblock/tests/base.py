"""
Vide xblock base classes.
"""
import unittest
import mock

from xblock.field_data import DictFieldData
from xblock.test.tools import TestRuntime

from video_xblock import VideoXBlock


class VideoXBlockTestBase(unittest.TestCase):
    """
    Base video_xblock test class.
    """

    def setUp(self):
        """
        Create a XBlock VideoXBlock for testing purpose.
        """
        super(VideoXBlockTestBase, self).setUp()
        runtime = TestRuntime()  # pylint: disable=abstract-class-instantiated
        self.xblock = VideoXBlock(
            runtime,
            DictFieldData(
                {'account_id': 'account_id', 'metadata': {'client_id': 'api_key', 'client_secret': 'api_secret'}}
            ),
            scope_ids=mock.Mock(spec=[])
        )

        # Mocked objects is a list containing info about mocked entities.
        # Example:
        # self.mocked_objects.append({
        #    'obj': requests,                      # object that contains entity to be mocked
        #    'attrs': ['get', ],                   # list of methods/fields to be mocked
        #    'value': [copy.copy(requests.get), ]  # save here original values
        # })
        self.mocked_objects = []

    def restore_mocked(self):
        """
        Restore state of mocked entities.
        """
        if self.mocked_objects:
            for original in self.mocked_objects:
                for index, attr in enumerate(original['attrs']):
                    setattr(original['obj'], attr, original['value'][index])
            self.mocked_objects = []

    def tearDown(self):
        """
        Restore mocked objects to default stay.
        """
        self.restore_mocked()
        super(VideoXBlockTestBase, self).tearDown()
