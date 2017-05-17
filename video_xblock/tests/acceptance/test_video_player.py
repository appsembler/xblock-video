"""
Acceptance test for video playback.
"""

from bok_choy.promise import EmptyPromise
from ddt import data, ddt
from xblockutils.base_test import SeleniumXBlockTest

from video_xblock.utils import loader
from video_xblock.tests.acceptance.pages import VideojsPlayerPage


@ddt
class TestStudentView(SeleniumXBlockTest):
    """
    Test the Student View of VideoXBlock.
    """

    def load_scenario(self, xml_file, params=None, load_immediately=True):
        """
        Given the name of an XML file in the xml_templates folder, load it into the workbench.
        """
        params = params or {}
        scenario = loader.load_unicode("workbench/scenarios/{}".format(xml_file))
        self.set_scenario_xml(scenario)
        if load_immediately:
            view = self.go_to_view("student_view")
            self.driver.switch_to.frame('xblock-video-player-usage_id')
            return view

    @data('brightcove.xml', 'youtube.xml', 'vimeo.xml', 'wistia.xml')
    def test_video_player_can_play_video(self, scenario):
        # Arrange
        wrapper = self.load_scenario(scenario)
        vjs_player = VideojsPlayerPage(self.driver)

        # Act
        self.assertIsNotNone(wrapper)
        self.assertFalse(vjs_player.is_playing())
        vjs_player.play_button.click()  # pylint: disable=no-member

        # Assert
        EmptyPromise(vjs_player.is_playing, "Video is being played").fulfill()
