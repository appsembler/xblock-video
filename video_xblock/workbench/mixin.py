"""
Workbench mixin adds XBlock SDK workbench runtime support.
"""

from video_xblock.utils import loader


class WorkbenchMixin(object):
    """
    WorkbenchMixin adds XBlock-SDK workbench support to an XBlock.
    """

    @staticmethod
    def workbench_scenarios():
        """
        Load scenarios for display in the workbench from xml files.
        """
        return loader.load_scenarios_from_path('workbench/scenarios')
