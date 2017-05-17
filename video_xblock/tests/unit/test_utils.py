"""
Test utils.
"""

import unittest
from ddt import ddt, data
from mock import patch, Mock, PropertyMock

from video_xblock.utils import import_from, underscore_to_mixedcase


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

    @patch('video_xblock.utils.import_module')
    def test_import_from(self, import_module_mock):
        import_module_mock.return_value = module_mock = Mock()
        type(module_mock).test_class = class_mock = PropertyMock(
            return_value='a_class'
        )

        self.assertEqual(import_from('test_module', 'test_class'), 'a_class')
        import_module_mock.assert_called_once_with('test_module')
        class_mock.assert_called_once_with()
