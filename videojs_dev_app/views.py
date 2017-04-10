"""
Django views.
"""
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.shortcuts import render

from utils import get_player, player_data

PLAYER_LIST = settings.PLAYER_DATA.keys()


def player_list(request):
    """
    View with list of players.
    """
    context = {'player_list': PLAYER_LIST}
    return render(request, 'list.html', context)


def detail(request, player_name):
    """
    View to render player.
    """
    data = player_data(player_name)
    player_cls = get_player(player_name)
    if not player_cls or not data:
        return HttpResponseNotFound(
            '<h1>404 Error. Unsupported player name. Choose one from list: %s</h1' % PLAYER_LIST
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
