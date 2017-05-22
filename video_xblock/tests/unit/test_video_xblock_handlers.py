"""
Test cases for VideoXBlock handlers
"""

import json
from mock import patch, Mock

from video_xblock import VideoXBlock
from video_xblock.tests.unit.base import VideoXBlockTestBase


def arrange_request_mock(request_body):
    """
    Helper factory to create request mocks
    """
    request_mock = Mock()
    request_mock.method = 'POST'
    request_mock.body = request_body
    return request_mock


class AuthenticateApiHandlerTests(VideoXBlockTestBase):
    """
    Test cases for `VideoXBlock.authenticate_video_api_handler`
    """

    @patch.object(VideoXBlock, 'authenticate_video_api')
    def test_auth_video_api_handler_delegates_call(self, auth_video_api_mock):
        # Arrange
        request_mock = arrange_request_mock('"test-token-123"')  # JSON string
        auth_video_api_mock.return_value = {}, ''

        # Act
        result_response = self.xblock.authenticate_video_api_handler(request_mock)
        result = result_response.body  # pylint: disable=no-member

        # Assert
        self.assertEqual(
            result,
            json.dumps({'success_message': 'Successfully authenticated to the video platform.'})
        )
        auth_video_api_mock.assert_called_once_with('test-token-123')  # Python string
