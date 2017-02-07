"""
RelativeTime field back-ported from xmodule.fields to avoid import error and travis testing complication.

Reference:
https://github.com/edx/edx-platform/blob/52beec887841b3b5aa132c9c14d967f7fb1d27f6/common/lib/xmodule/xmodule/fields.py#L139

"""

import datetime
import time

from xblock.fields import JSONField


class RelativeTime(JSONField):
    """
    Field for start_time and end_time video module properties.

    It was decided, that python representation of start_time and end_time
    should be python datetime.timedelta object, to be consistent with
    common time representation.

    At the same time, serialized representation should be "HH:MM:SS"
    This format is convenient to use in XML (and it is used now),
    and also it is used in frond-end studio editor of video module as format
    for start and end time fields.

    In database we previously had float type for start_time and end_time fields,
    so we are checking it also.

    Python object of RelativeTime is datetime.timedelta.
    JSONed representation of RelativeTime is "HH:MM:SS"
    """
    # Timedeltas are immutable, see http://docs.python.org/2/library/datetime.html#available-types
    MUTABLE = False

    @classmethod
    def isotime_to_timedelta(cls, value):
        """
        Validate that value in "HH:MM:SS" format and convert to timedelta.

        Validate that user, that edits XML, sets proper format, and
         that max value that can be used by user is "23:59:59".
        """
        try:
            obj_time = time.strptime(value, '%H:%M:%S')
        except ValueError as error:
            raise ValueError(
                "Incorrect RelativeTime value {!r} was set in XML or serialized. "
                "Original parse message is {}".format(value, error.message)
            )
        return datetime.timedelta(
            hours=obj_time.tm_hour,
            minutes=obj_time.tm_min,
            seconds=obj_time.tm_sec
        )

    def from_json(self, value):
        """
        Convert value is in 'HH:MM:SS' format to datetime.timedelta.

        If not value, returns 0.
        If value is float (backward compatibility issue), convert to timedelta.
        """
        if not value:
            return datetime.timedelta(seconds=0)

        if isinstance(value, datetime.timedelta):
            return value

        # We've seen serialized versions of float in this field
        if isinstance(value, float):
            return datetime.timedelta(seconds=value)

        if isinstance(value, basestring):
            return self.isotime_to_timedelta(value)

        msg = "RelativeTime Field {0} has bad value '{1!r}'".format(self.name, value)
        raise TypeError(msg)

    def to_json(self, value):
        """
        Convert datetime.timedelta to "HH:MM:SS" format.

        If not value, return "00:00:00"

        Backward compatibility: check if value is float, and convert it. No exceptions here.

        If value is not float, but is exceed 23:59:59, raise exception.
        """
        if not value:
            return "00:00:00"

        if isinstance(value, float):  # backward compatibility
            value = min(value, 86400)
            return self.timedelta_to_string(datetime.timedelta(seconds=value))

        if isinstance(value, datetime.timedelta):
            if value.total_seconds() > 86400:  # sanity check
                raise ValueError(
                    "RelativeTime max value is 23:59:59=86400.0 seconds, "
                    "but {} seconds is passed".format(value.total_seconds())
                )
            return self.timedelta_to_string(value)

        raise TypeError("RelativeTime: cannot convert {!r} to json".format(value))

    def timedelta_to_string(self, value):
        """
        Makes first 'H' in str representation non-optional.

        str(timedelta) has [H]H:MM:SS format, which is not suitable
        for front-end (and ISO time standard), so we force HH:MM:SS format.
        """
        stringified = str(value)
        if len(stringified) == 7:
            stringified = '0' + stringified
        return stringified

    def enforce_type(self, value):
        """
        Ensure that when set explicitly the Field is set to a timedelta
        """
        if isinstance(value, datetime.timedelta) or value is None:
            return value

        return self.from_json(value)
