"""
Test utils.
"""
import types
import unittest

from ddt import ddt, data
from mock import patch, Mock, PropertyMock

from video_xblock.constants import TranscriptSource
from video_xblock.utils import (
    import_from, underscore_to_mixedcase, create_reference_name, normalize_transcripts, filter_transcripts_by_source
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
        for string, expected_result in list(test_data.items()):
            self.assertEqual(underscore_to_mixedcase(string), expected_result)

    @patch('video_xblock.utils.import_module')
    def test_import_from(self, import_module_mock):
        """
        Test module importing function.
        """
        import_module_mock.return_value = module_mock = Mock()
        type(module_mock).test_class = class_mock = PropertyMock(
            return_value='a_class'
        )

        self.assertEqual(import_from('test_module', 'test_class'), 'a_class')
        import_module_mock.assert_called_once_with('test_module')
        class_mock.assert_called_once_with()

    def test_create_reference_name(self):
        """
        Test file reference created in given format.
        """
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
        """
        Test abnormal transcripts became normalized.
        """
        # Arrange
        test_transcripts = [{'source': 'default'}, {}]
        expected_transcripts = [{'source': 'default'}, {'source': 'manual'}]
        # Act
        normalized_transcripts = normalize_transcripts(test_transcripts)
        # Assert
        self.assertEqual(normalized_transcripts, expected_transcripts)

    def test_normalize_transcripts_normal(self):
        """
        Test normal transcripts stay normal after normalizing.
        """
        # Arrange
        test_transcripts = [{'source': 'default'}, {'source': 'some_else'}]
        expected_transcripts = [{'source': 'default'}, {'source': 'some_else'}]
        # Act
        normalized_transcripts = normalize_transcripts(test_transcripts)
        # Assert
        self.assertEqual(normalized_transcripts, expected_transcripts)

    def test_filter_transcripts_by_source_empty(self):
        """
        Test transcripts filtering can handle empty transcripts set.
        """
        # Arrange
        test_transcripts = []

        # Act
        filtered_transcripts = filter_transcripts_by_source(test_transcripts)

        # Assert
        self.assertIsInstance(filtered_transcripts, list)
        self.assertListEqual(filtered_transcripts, test_transcripts)

    def test_filter_transcripts_by_source_by_default(self):
        """
        Test transcripts filtering works with default filtering configuration.
        """
        # Arrange
        default_transcripts = [{'id': 'DT1', 'source': 'default'}, {'id': 'DT2', 'source': 'default'}]
        manual_transcripts = [{'id': 'MT1', 'source': 'manual'}, {'id': 'MT2', 'source': 'manual'}]
        three_pm_transcripts = [{'id': 'PM1', 'source': '3play-media'}, {'id': 'PM2', 'source': '3play-media'}]
        test_transcripts = default_transcripts + manual_transcripts + three_pm_transcripts

        # Act
        filtered_transcripts = filter_transcripts_by_source(test_transcripts)

        # Assert
        self.assertIsInstance(filtered_transcripts, types.GeneratorType)
        self.assertListEqual(list(filtered_transcripts), default_transcripts)

    def test_filter_transcripts_by_source_exclude(self):
        """
        Test transcripts filtering `exclude` mode works.
        """
        # Arrange
        default_transcripts = [{'id': 'DT1', 'source': 'default'}, {'id': 'DT2', 'source': 'default'}]
        manual_transcripts = [{'id': 'MT1', 'source': 'manual'}, {'id': 'MT2', 'source': 'manual'}]
        three_pm_transcripts = [{'id': 'PM1', 'source': '3play-media'}, {'id': 'PM2', 'source': '3play-media'}]
        test_transcripts = default_transcripts + manual_transcripts + three_pm_transcripts

        # Act
        filtered_transcripts = filter_transcripts_by_source(
            test_transcripts, sources=[TranscriptSource.DEFAULT, TranscriptSource.MANUAL], exclude=True
        )

        # Assert
        self.assertIsInstance(filtered_transcripts, types.GeneratorType)
        self.assertListEqual(list(filtered_transcripts), three_pm_transcripts)
