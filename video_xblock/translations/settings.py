"""
Django settings for making translations with help of statici18n.
See documentation here http://django-statici18n.readthedocs.io/en/latest/settings.html
"""

from __future__ import absolute_import
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', '",cB3Jr.?xu[x_Ci]!%HP>#^AVmWi@r/W3u,w?pY+~J!R>;WN+,3}Sb{K=Jp~;&k')

# SECURITY WARNING: don't run with debug turned on in production!
# This is just a container for running tests
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'statici18n',
    'video_xblock',
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
STATIC_URL = '/static/'

LANGUAGES = [
    ('en', 'English'),
    # add supported languages here
]

STATICI18N_DOMAIN = 'text'
STATICI18N_PACKAGES = (
    'video_xblock',
)
STATICI18N_ROOT = 'video_xblock/static/js'
STATICI18N_OUTPUT_DIR = 'translations'
