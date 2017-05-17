"""
Page objects to use in tests.
"""

from video_xblock.tests.acceptance.element import IdPageElement, ClassPageElement


class VideoJsPlayerElement(IdPageElement):
    """
    Root VideoJs player element.
    """

    locator = 'video_player_block_id'


class VideoJsPlayButton(ClassPageElement):
    """
    VideoJs play button located on the control bar.
    """

    locator = 'vjs-play-control'


class VideojsPlayerPage(object):
    """
    VideoJs player page-object.
    """

    player_element = VideoJsPlayerElement()
    # player_element = VideoJsPlayerElement(usage_id=usage_id)
    play_button = VideoJsPlayButton()

    def __init__(self, driver):
        """Constructor."""
        self.driver = driver

    def is_playing(self):
        """
        Check if video is being played.
        """
        return 'vjs-playing' in self.player_element.get_attribute('class')  # pylint: disable=no-member
