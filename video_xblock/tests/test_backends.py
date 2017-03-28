"""
Test cases for video_xblock backends.
"""
# copy should be imported before requests
import babelfish
from ddt import ddt, data, unpack
from lxml import etree
from django.test.utils import override_settings
from xblock.core import XBlock
from video_xblock.settings import ALL_LANGUAGES
from video_xblock.utils import ugettext as _
from video_xblock.exceptions import VideoXBlockException
from video_xblock.tests.base import VideoXBlockTestBase
from video_xblock.backends import (
    brightcove,
    html5,
    wistia,
    youtube,
    vimeo
)
from video_xblock.tests.mocks import (
    brightcove as brightcove_mock,
    vimeo as vimeo_mock,
    wistia as wistia_mock,
    youtube as youtube_mock
)


@ddt
class TestCustomBackends(VideoXBlockTestBase):
    """
    Unit tests for custom video xblock backends.
    """
    backends = ['youtube', 'brightcove', 'wistia', 'vimeo', 'html5']

    auth_mocks = [
        youtube_mock.YoutubeAuthMock,
        brightcove_mock.BrightcoveAuthMock,
        wistia_mock.WistiaAuthMock,
        vimeo_mock.VimeoAuthMock,
    ]

    default_trans_mocks = [
        youtube_mock.YoutubeDefaultTranscriptsMock,
        brightcove_mock.BrightcoveDefaultTranscriptsMock,
        wistia_mock.WistiaDefaultTranscriptsMock,
        vimeo_mock.VimeoDefaultTranscriptsMock,
    ]

    download_transcript_mocks = [
        youtube_mock.YoutubeDownloadTranscriptMock,
        brightcove_mock.BrightcoveDownloadTranscriptMock,
        wistia_mock.WistiaDownloadTranscriptMock,
        vimeo_mock.VimeoDownloadTranscriptMock,
    ]

    @XBlock.register_temp_plugin(brightcove.BrightcovePlayer, 'brightcove')
    @XBlock.register_temp_plugin(wistia.WistiaPlayer, 'wistia')
    @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    @XBlock.register_temp_plugin(vimeo.VimeoPlayer, 'vimeo')
    @XBlock.register_temp_plugin(html5.Html5Player, 'html5')
    def setUp(self):
        super(TestCustomBackends, self).setUp()
        self.player = {}
        for backend in self.backends:
            player_class = XBlock.load_class(backend)
            self.player[backend] = player_class

    def test_get_player_html(self):
        """
        Check that player files content is returned in Response body.
        """
        context = {
            'player_state': {
                'transcripts': [{
                    'lang': 'en',
                    'label': 'English',
                    'url': 'http://test.url'
                }],
                'currentTime': ''
            },
            'url': 'https://example.com/video.mp4',
            'start_time': '',
            'end_time': ''
        }
        for backend in self.backends:
            player = self.player[backend]
            res = player(self.xblock).get_player_html(**context)
            self.assertIn('window.videojs', res.body)

    expected_basic_fields = [
        ('display_name', 'href'),
        ('display_name', 'href', 'account_id'),
        ('display_name', 'href'),
        ('display_name', 'href'),
        ('display_name', 'href'),
    ]

    expected_advanced_fields = [
        (
            'start_time', 'end_time', 'handout', 'transcripts',
            'threeplaymedia_file_id', 'threeplaymedia_apikey', 'download_transcript_allowed',
            'default_transcripts', 'download_video_allowed', 'download_video_url'
        ),
        (
            'player_id', 'start_time', 'end_time', 'handout', 'transcripts',
            'threeplaymedia_file_id', 'threeplaymedia_apikey', 'download_transcript_allowed',
            'default_transcripts', 'download_video_allowed', 'download_video_url'
        ),
        (
            'start_time', 'end_time', 'handout', 'transcripts',
            'threeplaymedia_file_id', 'threeplaymedia_apikey', 'download_transcript_allowed',
            'default_transcripts', 'download_video_allowed', 'download_video_url'
        ),
        (
            'start_time', 'end_time', 'handout', 'transcripts',
            'threeplaymedia_file_id', 'threeplaymedia_apikey', 'download_transcript_allowed',
            'default_transcripts', 'download_video_allowed', 'download_video_url'
        ),
        (
            'start_time', 'end_time', 'handout', 'transcripts',
            'threeplaymedia_file_id', 'threeplaymedia_apikey', 'download_transcript_allowed',
            'download_video_allowed',
        ),
    ]

    @data(*zip(backends, expected_basic_fields, expected_advanced_fields))
    @unpack
    def test_basic_advanced_fields(self, backend, expected_basic_fields, expected_advanced_fields):
        """
        Test basic_fields & advanced_fields for {0} backend
        """
        player = self.player[backend](self.xblock)
        self.assertTupleEqual(player.basic_fields, expected_basic_fields)
        self.assertTupleEqual(player.advanced_fields, expected_advanced_fields)

    @data(
        ([{'lang': 'ru'}], [{'lang': 'en'}, {'lang': 'uk'}]),
        ([{'lang': 'en'}, {'lang': 'uk'}], [{'lang': 'ru'}]),
        ([{'lang': 'some_other_lng'}], [{'lang': 'en'}, {'lang': 'ru'}, {'lang': 'uk'}])
    )
    @unpack
    def test_filter_default_transcripts(self, transcripts, default):
        """
        Check transcripts are excluded from the list of available ones in video xblock.
        """
        default_transcripts = [{'lang': 'en'}, {'lang': 'ru'}, {'lang': 'uk'}]
        for backend in self.backends:
            player = self.player[backend](self.xblock)
            res = player.filter_default_transcripts(default_transcripts, transcripts)
            self.assertEqual(res, default)

    @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
    @data(
        ('en', 'English'),
        ('to', 'Tonga (Tonga Islands)'),
        ('unknown', ''))
    @unpack
    def test_get_transcript_language_parameters(self, lng_abbr, lng_name):
        """
        Check parameters of the transcript's language.
        """
        for backend in self.backends:
            player = self.player[backend](self.xblock)
            try:
                res = player.get_transcript_language_parameters(lng_abbr)
                self.assertEqual(res, (lng_abbr, lng_name))
            except VideoXBlockException as ex:
                self.assertIn(_('Not all the languages of transcripts fetched from video platform'), ex.message)

    media_ids = [
        '44zaxzFsthY', '45263567468485', 'HRrr784kH8932Z', '202889234',
        'https://example.com/sample.mp4'
    ]
    media_urls = [
        'https://www.youtube.com/watch?v=44zaxzFsthY',
        'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
        'https://wi.st/medias/HRrr784kH8932Z',
        'https://vimeo.com/202889234',
        'https://example.com/sample.mp4',
    ]

    @data(*zip(backends, media_urls, media_ids))
    @unpack
    def test_media_id(self, backend, url, expected_media_id):
        """
        Check that media id is extracted from the video url for {0} backend
        """
        player = self.player[backend](self.xblock)
        res = player.media_id(url)
        self.assertEqual(res, expected_media_id)

    @data(*zip(backends, media_urls))
    @unpack
    def test_match(self, backend, url):
        """
        Check if provided video `href` validates in right way for {0} backend
        """
        player = self.player[backend]
        res = player.match(url)
        self.assertTrue(bool(res))

        # test wrong data
        res = player.match('http://wrong.url')
        self.assertFalse(bool(res))

    @data(*zip(backends, ['some_token'] * len(backends), auth_mocks))
    @unpack
    def test_authenticate_api(self, backend, token, auth_mock):
        """
        Check that backend can successfully pass authentication.
        """
        player = self.player[backend]
        for event in auth_mock.get_outcomes():
            mock = auth_mock(event=event)
            self.mocked_objects = mock.apply_mock(self.mocked_objects)
            try:
                auth_data, error = res = player(self.xblock).authenticate_api(
                    **{'token': token, 'account_id': 45263567468485}
                )
                expected_auth_data = mock.expected_value[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(auth_data, expected_auth_data)
            except VideoXBlockException as ex:
                error = ex.message
            expected_error = mock.expected_value[-1]
            self.assertIn(expected_error, error)

    @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
    @data(*(zip(backends, media_ids, default_trans_mocks)))
    @unpack
    def test_get_default_transcripts(self, backend, media_id, trans_mock):
        """
        Check getting list of default transcripts.
        """
        player = self.player[backend]
        for event in trans_mock.get_outcomes():
            mock = trans_mock(event=event, xblock=self.xblock, mock_magic=self.xblock.metadata)
            self.mocked_objects = mock.apply_mock(self.mocked_objects)
            try:
                default_transcripts, message = res = player(self.xblock).get_default_transcripts(video_id=media_id)
                expected_default_transcripts = mock.expected_value[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(default_transcripts, expected_default_transcripts)
            except brightcove.BrightcoveApiClientError as ex:
                message = ex.message
            except babelfish.converters.LanguageReverseError:
                message = 'LanguageReverseError'
            expected_message = mock.expected_value[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()

    @data(
        *(
            zip(
                backends,
                download_transcript_mocks,
                [  # params
                    (  # youtube
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': ''},
                        {'url': 'http://example.com', 'language_code': ''}
                    ),
                    (  # brightcove
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': 'en'}
                    ),
                    (  # wistia
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': 'en'},
                        {'url': 'http://example.com', 'language_code': 'uk'}
                    ),
                    (  # vimeo
                        {'url': None, 'language_code': None},
                    )
                ],
            )
        )
    )
    @unpack
    def test_download_default_transcript(self, backend, download_transcript_mock, params):
        """
        Check default transcript is downloaded from a video platform API.
        """
        player = self.player[backend]
        for index, event in enumerate(download_transcript_mock.get_outcomes()):
            mock = download_transcript_mock(event=event)
            self.mocked_objects = mock.apply_mock(self.mocked_objects)
            try:
                res = player(self.xblock).download_default_transcript(**params[index])
                message = ''
                expected_default_transcript = mock.expected_value[0]
                self.assertIsInstance(res, unicode)
                self.assertEqual(res, expected_default_transcript)
            except VideoXBlockException as ex:
                message = ex.message
            except etree.XMLSyntaxError:
                message = 'XMLSyntaxError exception'
            expected_message = mock.expected_value[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()
