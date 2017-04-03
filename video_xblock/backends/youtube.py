# -*- coding: utf-8 -*-
"""
YouTube Video player plugin.
"""

import HTMLParser
import json
import httplib
import re
import textwrap
import urllib

import requests
from lxml import etree

from video_xblock import BaseVideoPlayer
from video_xblock.utils import ugettext as _
from video_xblock.exceptions import VideoXBlockException


class YoutubePlayer(BaseVideoPlayer):
    """
    YoutubePlayer is used for videos hosted on the Youtube.com.
    """

    # Regex is taken from http://regexr.com/3a2p0
    url_re = re.compile(
        r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)(?P<media_id>[a-zA-Z0-9_-]{6,11})'
    )

    # YouTube API for requesting transcripts.
    # For example: http://video.google.com/timedtext?lang=en&v=QLQ-85Td2Gs
    captions_api = {
        'url': 'video.google.com/timedtext',
        'params': {
            'v': 'set_video_id_here',
            'lang': 'en',  # not mandatory
            'name': ''     # not mandatory
        },
        'response': {
            'language_code': 'lang_code',
            'language_label': 'lang_translated',
            'subs': 'text'
        }
    }

    # Stores default transcripts fetched from the Youtube captions API
    default_transcripts = []

    def media_id(self, href):
        """
        Extract Platform's media id from the video url.
        """
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['data_setup'] = json.dumps(YoutubePlayer.player_data_setup(context))

        frag = super(YoutubePlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/youtube.html', **context)
        )

        js_files = [
            'static/vendor/js/Youtube.min.js',
            'static/vendor/js/videojs-offset.min.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @staticmethod
    def player_data_setup(context):
        """
        Youtube Player data setup.
        """
        result = BaseVideoPlayer.player_data_setup(context)
        result.update({
            "techOrder": ["youtube"],
            "sources": [{
                "type": "video/youtube",
                "src": context['url']
            }],
            "youtube": {"iv_load_policy": 1},
        })
        return result

    def fetch_default_transcripts_languages(self, video_id):
        """
        Fetch available transcripts languages from a Youtube server.

        Reference to `youtube_video_transcript_name()`:
            https://github.com/edx/edx-platform/blob/ecc3473d36b3c7a360e260f8962e21cb01eb1c39/common/lib/xmodule/xmodule/video_module/transcripts_utils.py#L97

        Arguments:
            video_id (str): Media id fetched from `href` field of studio-edit modal.
        Returns:
            available_languages (list): List of pairs of codes and labels of captions' languages fetched from API,
                together with transcripts' names if any.
                If the transcript name is not empty on youtube server we have to pass
                name param in url in order to get transcript.
                Example: http://video.google.com/timedtext?lang=en&v={video_id}&name={transcript_name}
            message (str): Message with status on captions API call.
        """
        utf8_parser = etree.XMLParser(encoding='utf-8')
        # This is to update self.captions_api with a video id.
        self.captions_api['params']['v'] = video_id
        transcripts_param = {'type': 'list', 'v': self.captions_api['params']['v']}
        available_languages = []
        message = ''

        try:
            data = requests.get('http://' + self.captions_api['url'], params=transcripts_param)
        except requests.exceptions.RequestException as exception:
            # Probably, current API has changed
            message = 'No timed transcript may be fetched from a video platform. ' \
                      'Error: {}'.format(str(exception))
            return available_languages, message

        if data.status_code == httplib.OK and data.text:
            youtube_data = etree.fromstring(data.content, parser=utf8_parser)
            empty_subs = False if [el.get('transcript_list') for el in youtube_data] else True
            available_languages = [
                [el.get('lang_code'), el.get('lang_translated'), el.get('name')]
                for el in youtube_data if el.tag == 'track'
            ]
            if empty_subs:
                message = 'For now, video platform doesn\'t have any timed transcript for this video.'
        else:
            message = 'No timed transcript may be fetched from a video platform.'

        return available_languages, message

    def get_default_transcripts(self, **kwargs):
        """
        Fetch transcripts list from a video platform.
        """
        # Fetch available transcripts' languages from API
        video_id = kwargs.get('video_id')
        available_languages, message = self.fetch_default_transcripts_languages(video_id)
        self.default_transcripts = []
        for lang_code, lang_translated, transcript_name in available_languages:  # pylint: disable=unused-variable
            self.captions_api['params']['lang'] = lang_code
            self.captions_api['params']['name'] = transcript_name
            transcript_url = 'http://{url}?{params}'.format(
                url=self.captions_api['url'],
                params=urllib.urlencode(self.captions_api['params'])
            )
            # Update default transcripts languages parameters in accordance with pre-configured language settings
            lang_code, lang_label = self.get_transcript_language_parameters(lang_code)
            self.default_transcripts.append({
                'lang': lang_code,
                'label': lang_label,
                'url': transcript_url,
            })
        return self.default_transcripts, message

    @staticmethod
    def format_transcript_timing(sec, period_type=None):
        """
        Convert seconds to timestamp of the format `hh:mm:ss:mss`, e.g. 00:00:03.887.

        Arguments:
            sec (str): Transcript timing in seconds with milliseconds resolution.
            period_type (str): Timing period type (whether `end` or `start`).
        """
        # Youtube returns transcripts with the equal endtime and startime for previous and next transcript blocks
        # respectively. That is why transcript blocks are overlapping. Get rid of it by decreasing timing on 0.001.
        float_sec = float(sec)
        sec = float_sec - 0.001 if period_type == 'end' and float_sec >= 0.001 else sec

        mins, secs = divmod(sec, 60)
        hours, mins = divmod(mins, 60)
        hours_formatted = str(int(hours)).zfill(2)
        mins_formatted = str(int(mins)).zfill(2)
        secs_formatted = str("{:06.3f}".format(round(secs, 3)))
        timing = "{}:{}:{}".format(
            hours_formatted,
            mins_formatted,
            secs_formatted
        )
        return timing

    def format_transcript_element(self, element, element_number):
        """
        Format transcript's element in order for it to be converted to WebVTT format.
        """
        sub_element = u"\n\n"
        html_parser = HTMLParser.HTMLParser()
        if element.tag == "text":
            start = float(element.get("start"))
            duration = float(element.get("dur", 0))  # dur is not mandatory
            text = element.text
            end = start + duration
            if text:
                formatted_start = self.format_transcript_timing(start)
                formatted_end = self.format_transcript_timing(end, 'end')
                timing = '{} --> {}'.format(formatted_start, formatted_end)
                text_encoded = text.encode('utf8', 'ignore')
                text = text_encoded.replace('\n', ' ')
                unescaped_text = html_parser.unescape(text.decode('utf8'))
                sub_element = u"""\
                {element_number}
                {timing}
                {unescaped_text}

                """.format(
                    element_number=element_number, timing=timing, unescaped_text=unescaped_text
                )
        return textwrap.dedent(sub_element)

    def download_default_transcript(self, url=None, language_code=None):  # pylint: disable=unused-argument
        """
        Download default transcript from Youtube API and format it to WebVTT-like unicode.

        Reference to `get_transcripts_from_youtube()`:
            https://github.com/edx/edx-platform/blob/ecc3473d36b3c7a360e260f8962e21cb01eb1c39/common/lib/xmodule/xmodule/video_module/transcripts_utils.py#L122
        """
        if url is None:
            raise VideoXBlockException(_('`url` parameter is required.'))
        utf8_parser = etree.XMLParser(encoding='utf-8')
        data = requests.get(url)
        xmltree = etree.fromstring(data.content, parser=utf8_parser)
        sub = [
            self.format_transcript_element(element, i)
            for i, element in enumerate(xmltree, 1)
        ]
        sub = "".join(sub)
        sub = u"WEBVTT\n\n" + unicode(sub) if "WEBVTT" not in sub else unicode(sub)
        return sub

    def dispatch(self, request, suffix):
        """
        Youtube dispatch method.
        """
        pass
