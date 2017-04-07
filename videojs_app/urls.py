"""
videojs_app URL Configuration.
"""
from django.conf.urls import url
from views import index
urlpatterns = [
    url(r'^(?P<player_name>[a-z0-9]+)$', index, name='index'),

]
