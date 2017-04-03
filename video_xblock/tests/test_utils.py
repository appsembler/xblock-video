"""
Test utils.
"""

import unittest
from ddt import ddt, data

from video_xblock.utils import underscore_to_mixedcase


@ddt
class UtilsTest(unittest.TestCase):
    """
    Test Utils.
    """

    @data({
        'test': 'test',
        'test_variable': 'testVariable',
        'long_test_variable': 'longTestVariable'
    })
    def test_underscore_to_mixedcase(self, test_data):
        """Test string conversion from underscore to mixedcase"""
        for string, expected_result in test_data.items():
            self.assertEqual(underscore_to_mixedcase(string), expected_result)
