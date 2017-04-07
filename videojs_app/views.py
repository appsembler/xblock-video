"""
Django views.
"""
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings

from utils import get_player, player_data


def index(request, player_name):
    """
    View to render player.
    """
    data = player_data(player_name)
    player_cls = get_player(player_name)
    if not player_cls or not data:
        player_list = ", ".join(settings.PLAYER_DATA.keys())
        return HttpResponseNotFound(
            '<h1>404 Error. Unsupported player name. Choose one from list: %s</h1' % player_list
        )
    player = player_cls(data)
    response = player.get_player_html(
        url=data['href'],
        autoplay=False,
        account_id='123',
        player_id='321',
        video_id=player.media_id(data['href']),
        video_player_id='video_player_{}'.format('block_id'),  # pylint: disable=no-member
        save_state_url='',
        player_state={
            'currentTime': 0,
            'transcripts': []
        },
        start_time=0,  # pylint: disable=no-member
        end_time=0,  # pylint: disable=no-member
        brightcove_js_url=0,
        transcripts={},
    )
    return HttpResponse(response.body)
