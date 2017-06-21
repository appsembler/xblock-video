"""
Test cases for constants entities.
"""

import unittest

from ddt import ddt, data
from video_xblock.constants import TPMApiLanguage


@ddt
class ConstantsTest(unittest.TestCase):
    """
    Test Constants.
    """

    def test_three_play_media_language_data_constant_creation(self):
        """Test 3PlayMedia available transcript language_info object creation"""
        self.assertRaises(ValueError, TPMApiLanguage, 'a')
        self.assertRaises(ValueError, TPMApiLanguage, 999)

    @data({
        1: {
            "ietf_code": "en",
            "iso_639_1_code": "en",
            "name": "English",
            "full_name": "English",
        },
        48: {
            "ietf_code": "",
            "iso_639_1_code": "uk",
            "name": "Ukrainian",
            "full_name": "Ukrainian",
        }
    })
    def test_three_play_media_language_data_constant_structure(self, test_data):
        """Test 3PlayMedia available transcript language_info object creation"""
        for lang_id, lang_info in test_data.items():
            self.assertEqual(TPMApiLanguage(lang_id).ietf_code, lang_info["ietf_code"])
            self.assertEqual(TPMApiLanguage(lang_id).iso_639_1_code, lang_info["iso_639_1_code"])
            self.assertEqual(TPMApiLanguage(lang_id).name, lang_info["name"])
            self.assertEqual(TPMApiLanguage(lang_id).full_name, lang_info["full_name"])
