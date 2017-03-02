"""
Custom, VideoXblock specific Exceptions.
"""

from __future__ import unicode_literals

from .utils import ugettext as _


class VideoXBlockException(Exception):
    """
    Base class for video xblock exceptions. Subclasses should provide `.default_msg` property.
    """

    default_msg = _('An exception occurred.')

    def __init__(self, detail=None):
        """
        Initialization of exceptions base class object.
        """
        self.detail = detail if detail is not None else self.default_msg
        super(VideoXBlockException, self).__init__(detail)

    def __str__(self):
        """
        Override string representation of exceptions base class object.
        """
        return self.detail


class VideoXBlockMockException(VideoXBlockException):
    """
    Base class for video xblock exceptions. Subclasses should provide `.default_msg` property.
    """

    default_msg = _('A Mock exception occurred.')


class ApiClientError(VideoXBlockException):
    """
    Base API client exception.
    """

    default_msg = _('API error occurred.')
