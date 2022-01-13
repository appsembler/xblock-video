"""
Test cases for VideoXBlock handlers
"""

import json

from mock import patch, Mock, PropertyMock

from video_xblock import VideoXBlock
from video_xblock.tests.unit.base import VideoXBlockTestBase, arrange_request_mock


class AuthenticateApiHandlerTests(VideoXBlockTestBase):  # pylint: disable=test-inherits-tests
    """
    Test cases for `VideoXBlock.authenticate_video_api_handler`.
    """

    @patch.object(VideoXBlock, 'authenticate_video_api')
    def test_auth_video_api_handler_delegates_call(self, auth_video_api_mock):
        """
        Test xBlock's video API authentication works properly.
        """
        # Arrange
        request_mock = arrange_request_mock('"test-token-123"')  # JSON string
        auth_video_api_mock.return_value = {}, ''

        # Act
        result_response = self.xblock.authenticate_video_api_handler(request_mock)
        result = result_response.body  # pylint: disable=no-member

        # Assert
        self.assertEqual(
            result,
            bytes(json.dumps({'success_message': 'Successfully authenticated to the video platform.'}), 'utf-8')
        )
        auth_video_api_mock.assert_called_once_with('test-token-123')  # Python string


class UploadDefaultTranscriptHandlerTests(VideoXBlockTestBase):  # pylint: disable=test-inherits-tests
    """
    Test cases for `VideoXBlock.upload_default_transcript_handler`.
    """

    @patch('video_xblock.video_xblock.create_reference_name')
    def test_upload_handler_default_transcript_not_in_vtt_case(self, create_reference_name_mock):
        """
        Test xBlock's handler for default transcripts uploading.
        """
        # Arrange
        request_body = """{"label": "test_label","lang": "test_lang","source": "test_source","url": "test_url"}"""
        assert_data = json.loads(request_body)
        test_media_id = 'test_video_id'
        test_subs_text = 'test_subs_text'
        test_reference = 'test_reference'
        test_file_name = 'test_file_name'
        test_external_url = 'test_external_url'

        request_mock = arrange_request_mock(request_body)
        create_reference_name_mock.return_value = test_reference

        with patch.object(self.xblock, 'get_player') as get_player_mock, \
                patch.object(self.xblock, 'convert_caps_to_vtt') as convert_caps_mock, \
                patch.object(self.xblock, 'create_transcript_file') as create_transcript_file_mock:

            get_player_mock.return_value = player_mock = Mock()
            convert_caps_mock.return_value = prepared_subs_mock = Mock()
            create_transcript_file_mock.return_value = (test_file_name, test_external_url)

            player_mock.media_id.return_value = test_media_id
            player_mock.download_default_transcript.return_value = test_subs_text
            type(player_mock).default_transcripts_in_vtt = PropertyMock(return_value=False)

            # Act
            response = self.xblock.upload_default_transcript_handler(request_mock)

            # Assert
            player_mock.download_default_transcript.assert_called_with(
                assert_data['url'], assert_data['lang']
            )
            create_reference_name_mock.assert_called_with(assert_data['label'], test_media_id, assert_data['source'])
            player_mock.download_default_transcript.assert_called_with(
                assert_data['url'], assert_data['lang']
            )
            convert_caps_mock.assert_called_with(caps=test_subs_text)
            create_transcript_file_mock.assert_called_with(trans_str=prepared_subs_mock, reference_name=test_reference)
            self.assertEqual(
                response.body,  # pylint: disable=no-member
                bytes(json.dumps({
                    'success_message': 'Successfully uploaded "test_file_name".',
                    'lang': assert_data['lang'],
                    'url': test_external_url,
                    'label': assert_data['label'],
                    'source': assert_data['source'],
                }), 'utf-8')
            )
