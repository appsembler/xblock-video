"""
Lists of constants that can be used in the video xblock.
"""


class status(object):  # pylint: disable=invalid-name
    """
    Contains HTTP codes used in video xblock.
    """

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_401_UNAUTHORIZED = 401
    HTTP_404_NOT_FOUND = 404


class PlayerName(object):
    """
    Contains Player names for each backends.
    """

    BRIGHTCOVE = 'brightcove-player'
    DUMMY = 'dummy-player'
    HTML5 = 'html5-player'
    VIMEO = 'vimeo-player'
    WISTIA = 'wistia-player'
    YOUTUBE = 'youtube-player'
