"""
Lists of constants that can be used in the video xblock.
"""


DEFAULT_LANG = 'en'


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
