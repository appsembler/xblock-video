"""
Unit tests for video_xblock modules.
"""
import django
from django.conf import settings

settings.configure(

    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
        },
    ]
)
django.setup()
