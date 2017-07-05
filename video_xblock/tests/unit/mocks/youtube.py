# -*- coding: utf-8 -*-
"""
Youtube backend mocks.
"""
from xblock.core import XBlock

from video_xblock.backends import youtube
from video_xblock.tests.unit.mocks.base import BaseMock, RequestsMock, ResponseStub


class YoutubeAuthMock(BaseMock):
    """
    Youtube auth mock class.
    """

    pass


class YoutubeDefaultTranscriptsMock(BaseMock):
    """
    Youtube default transcripts mock class.
    """

    _available_languages = [
        (u'en', u'English', u''),
        (u'uk', u'Українська', u'')
    ]

    _default_transcripts = [
        {'label': u'English', 'lang': u'en', 'source': u'default',
         'url': 'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here'},
        {'label': u'Ukrainian', 'lang': u'uk', 'source': u'default',
         'url': 'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here'}
    ]

    outcomes = (
        (
            'status_not_200',
            {
                'available_languages': [],
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'empty_subs',
            {
                'available_languages': _available_languages,
                'default_transcripts': _default_transcripts,
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'cant_fetch_data',
            {
                'available_languages': [],
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'success',
            {
                'available_languages': _available_languages,
                'default_transcripts': _default_transcripts,
                'message': ''
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def fetch_default_transcripts_languages(self):
        """
        Mock `fetch_default_transcripts_languages` returned value.
        """
        self.return_value = (
            self.ordered_results[self.event]['available_languages'], self.ordered_results[self.event]['message']
        )
        return self

    @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    def apply_mock(self, mocked_objects):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        player = XBlock.load_class('youtube')
        mocked_objects.append({
            'obj': player,
            'attrs': ['fetch_default_transcripts_languages'],
            'value': [player.fetch_default_transcripts_languages, ]
        })
        player.fetch_default_transcripts_languages = self.fetch_default_transcripts_languages()
        return mocked_objects


class YoutubeDownloadTranscriptMock(RequestsMock):
    """
    Youtube download default transcript mock class.
    """

    _vtt = u"""WEBVTT

1
00:00:00.000 --> 00:00:01.679
[INTRODUZIONE]

2
00:00:03.093 --> 00:00:06.392
Oggi voglio parlare di sottotitoli, di nuovo.

3
00:00:06.400 --> 00:00:10.811
Come sapete, io sono una grande sostenitrice dei sottotitoli su YouTube.

4
00:00:10.812 --> 00:00:13.290
Forse me la canto e me la suono da sola un po',

"""

    _xml = (
        '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="0" dur="1.68">[INTRODUZIONE]</text>'
        '<text start="3.093" dur="3.3">Oggi voglio parlare di\nsottotitoli, di nuovo.</text>'
        '<text start="6.4" dur="4.412">Come sapete, io sono una grande\nsostenitrice dei sottotitoli su YouTube.</text>'
        '<text start="10.812" dur="2.479">Forse me la canto e me la suono da sola un po&amp;#39;,</text></transcript>'
    )

    outcomes = (
        ('wrong_arguments', {'transcript': [], 'message': '`url` parameter is required.'}),
        ('no_xml_data', {'transcript': [], 'message': 'XMLSyntaxError exception'}),
        ('success', {'transcript': _vtt, 'message': ''})
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'no_xml_data':
            self.return_value = ResponseStub(status_code=200, body='{}')
        else:
            self.return_value = ResponseStub(status_code=200, body=self._xml)
        return lambda x: self.return_value
