from mock import Mock, patch
import unittest

from xblock.runtime import KvsFieldData, DictKeyValueStore
from xblock.test.tools import (
    assert_in, assert_equals, assert_true, assert_false, TestRuntime
)

from wistiavideo import WistiaVideoXBlock


class WistiaXblockBaseTests(object):
    def make_xblock(self):
        key_store = DictKeyValueStore()
        field_data = KvsFieldData(key_store)
        runtime = TestRuntime(services={'field-data': field_data})
        xblock = WistiaVideoXBlock(runtime, scope_ids=Mock())
        return xblock


class WistiaXblockTests(WistiaXblockBaseTests, unittest.TestCase):
    def test_media_id_property(self):
        xblock = self.make_xblock()
        xblock.href = 'https://example.wistia.com/medias/12345abcde'
        assert_equals(xblock.media_id, '12345abcde')

    def test_student_view(self):
        xblock = self.make_xblock()

        student_view_html = xblock.student_view()
        assert_in(xblock.media_id, student_view_html.body_html())


class WistiaXblockValidationTests(WistiaXblockBaseTests, unittest.TestCase):
    def test_validate_correct_inputs(self):
        xblock = self.make_xblock()

        for href in ('',
                     'https://foo.wistia.com/medias/bar',
                     'https://foo.wistia.com/embed/bar',
                     'https://foo.wi.st/embed/bar',
                     'https://foo.wi.st/medias/bar'):
            data = Mock(href=href)
            validation = Mock()
            validation.add = Mock()
            xblock.validate_field_data(validation, data)

            assert_false(validation.add.called)

    @patch('xblock.validation.ValidationMessage')
    def test_validate_incorrect_inputs(self, ValidationMessage):
        xblock = self.make_xblock()

        data = Mock(href='http://youtube.com/watch?v=something')
        validation = Mock()
        validation.add = Mock()

        xblock.validate_field_data(validation, data)
        assert_true(validation.add.called)
