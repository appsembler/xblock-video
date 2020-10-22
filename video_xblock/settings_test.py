"""
Test settings.
"""
from django.conf.global_settings import * # pylint: disable=wildcard-import


# It's needed to specify Django templates backend
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]
