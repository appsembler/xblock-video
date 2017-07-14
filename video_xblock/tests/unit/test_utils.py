"""
Test utils.
"""
import unittest

from ddt import ddt, data
from mock import patch, Mock, PropertyMock

from video_xblock.utils import (
    import_from, underscore_to_mixedcase, create_reference_name, normalize_transcripts
)


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
        """
        Test string conversion from underscore to mixedcase
        """
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

    def test_create_reference_name(self):
        # Arrange:
        lang_label = 'test_lang_label'
        video_id = 'test_video_id'
        source = 'test_source'
        expected_ref = 'test_lang_label_test_source_captions_video_test_video_id'
        # Act:
        reference = create_reference_name(lang_label, video_id, source)
        # Assert:
        self.assertEqual(reference, expected_ref)

    def test_normalize_transcripts_abnormal(self):
        # Arrange
        test_transcripts = [{'source': 'default'}, {}]
        expected_transcripts = [{'source': 'default'}, {'source': 'manual'}]
        # Act
        normalized_transcripts = normalize_transcripts(test_transcripts)
        # Assert
        self.assertEqual(normalized_transcripts, expected_transcripts)

    def test_normalize_transcripts_normal(self):
        # Arrange
        test_transcripts = [{'source': 'default'}, {'source': 'some_else'}]
        expected_transcripts = [{'source': 'default'}, {'source': 'some_else'}]
        # Act
        normalized_transcripts = normalize_transcripts(test_transcripts)
        # Assert
        self.assertEqual(normalized_transcripts, expected_transcripts)
