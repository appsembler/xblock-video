"""
VideoXBlock mixins moudle.
"""
from xblock.core import XBlock


@XBlock.wants('settings')
class SettingsMixin(XBlock):
    """
    SettingsMixin provides access to XBlock settings service.

    Provides convenient access to XBlock's settings set in edx-platform config files.

    Sample default settings in /edx/app/edxapp/cms.env.json:
    "XBLOCK_SETTINGS": {
      "video_xblock": {
        "3playmedia_api_key": "987654321",
        "account_id": "1234567890"
      }
    }
    """

    block_settings_key = 'video_xblock'

    @property
    def settings(self):
        """
        Return xblock settings set in .json config.

        Returned value depends on the context:
        - `studio_view()` is being executed in CMS context and gets data from `lms.env.json`.
        - `student_view` is being executed in LMS context and gets data from `lms.env.json`.

        Returns:
            dict: Settings from config file. E.g.
                {
                    "threeplaymedia_apikey": "987654321",
                    "account_id": "1234567890"
                }
        """
        s_service = self.runtime.service(self, 'settings')
        if s_service:
            # At the moment SettingsService is not available in the context
            # of Studio Edit modal. See https://github.com/edx/edx-platform/pull/14648
            return s_service.get_settings_bucket(self)
        else:
            from django.conf import settings
            return settings.XBLOCK_SETTINGS.get(self.block_settings_key, {})

    def populate_default_values(self, fields_dict):
        """
        Populate unset default values from settings file.
        """
        for key, value in self.settings.items():
            fields_dict.setdefault(key, value)
        return fields_dict
