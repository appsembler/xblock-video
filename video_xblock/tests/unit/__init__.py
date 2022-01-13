"""
Unit tests for video_xblock modules.
"""
import django
from django.conf import settings
from video_xblock import settings_test

settings.configure(default_settings=settings_test, DEBUG=True)
django.setup()
