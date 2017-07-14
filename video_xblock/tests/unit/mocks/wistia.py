"""
Wistia backend mocks.
"""

from video_xblock.tests.unit.mocks.base import RequestsMock, ResponseStub


class WistiaAuthMock(RequestsMock):
    """
    Wistia auth mock class.
    """

    return_value = ResponseStub(status_code=200, body='')

    outcomes = (
        (
            'not_authorized',
            {'auth_data': {'token': 'some_token'}, 'error_message': 'Authentication failed.'}
        ),
        (
            'success',
            {'auth_data': {'token': 'some_token'}, 'error_message': ''}
        )
    )

    to_return = ['auth_data', 'error_message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'not_authorized':
            self.return_value = ResponseStub(status_code=401)
        return lambda x: self.return_value
