"""
Test cases for video_xblock backends.
"""
import unittest

import babelfish
import requests
from ddt import ddt, data, unpack
from django.test.utils import override_settings
from lxml import etree
from mock import PropertyMock, Mock, patch
from xblock.core import XBlock

from video_xblock.backends import (
    base,
    brightcove,
    html5,
    wistia,
    youtube,
    vimeo,
)
from video_xblock.constants import TranscriptSource
from video_xblock.exceptions import VideoXBlockException
from video_xblock.settings import ALL_LANGUAGES
from video_xblock.tests.unit.base import VideoXBlockTestBase
from video_xblock.tests.unit.mocks import (
    brightcove as brightcove_mock,
    vimeo as vimeo_mock,
    wistia as wistia_mock,
    youtube as youtube_mock,
)
from video_xblock.tests.unit.mocks.base import ResponseStub
from video_xblock.utils import ugettext as _


class TestBaseBackendFunctionality(unittest.TestCase):
    """
    Unit tests for base video xblock backend.
    """

    def setUp(self):
        base.BaseVideoPlayer.__abstractmethods__ = set()  # the way we can instantiate abstract class during testing
        self.base_player = base.BaseVideoPlayer(xblock=Mock())  # pylint: disable=abstract-class-instantiated

    def test_base_player(self):
        """
        Cover BaseVideoPlayer initial functionality.
        """
        self.assertFalse(self.base_player.default_transcripts_in_vtt)
        self.assertEqual(self.base_player.media_id(href=Mock()), "")


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
        vimeo_mock.VimeoDefaultTranscriptsMock,
    ]

    download_transcript_mocks = [
        youtube_mock.YoutubeDownloadTranscriptMock,
        brightcove_mock.BrightcoveDownloadTranscriptMock,
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
        ['display_name', 'href'],
        ['display_name', 'href', 'account_id'],
        ['display_name', 'href'],
        ['display_name', 'href'],
        ['display_name', 'href'],
    ]

    expected_advanced_fields = [
        [  # Youtube
            'start_time', 'end_time', 'handout', 'download_transcript_allowed',
            'download_video_allowed', 'download_video_url'
        ],
        [  # Brightcove
            'player_id', 'start_time', 'end_time', 'handout',
            'download_transcript_allowed', 'download_video_allowed', 'download_video_url'
        ],
        [  # Wistia
            'start_time', 'end_time', 'handout',
            'download_transcript_allowed', 'download_video_allowed', 'download_video_url'
        ],
        [  # Vimeo
            'start_time', 'end_time', 'handout',
            'download_transcript_allowed', 'download_video_allowed', 'download_video_url'
        ],
        [  # Html5
            'start_time', 'end_time', 'handout',
            'download_transcript_allowed', 'download_video_allowed',
        ],
    ]

    @data(*zip(backends, expected_basic_fields, expected_advanced_fields))
    @unpack
    def test_basic_advanced_fields(self, backend, expected_basic_fields, expected_advanced_fields):
        """
        Test basic_fields & advanced_fields for {0} backend
        """
        player = self.player[backend](self.xblock)
        self.assertListEqual(player.basic_fields, expected_basic_fields)
        self.assertListEqual(player.advanced_fields, expected_advanced_fields)

    expected_3pm_fields = [
        ['threeplaymedia_file_id', 'threeplaymedia_apikey', 'threeplaymedia_streaming'],
        ['threeplaymedia_file_id', 'threeplaymedia_apikey', 'threeplaymedia_streaming'],
        ['threeplaymedia_file_id', 'threeplaymedia_apikey', 'threeplaymedia_streaming'],
        ['threeplaymedia_file_id', 'threeplaymedia_apikey', 'threeplaymedia_streaming'],
        ['threeplaymedia_file_id', 'threeplaymedia_apikey', 'threeplaymedia_streaming'],
    ]

    expected_trans_fields = [
        ['transcripts', 'default_transcripts'],
        ['transcripts', 'default_transcripts', 'token'],
        ['transcripts', 'default_transcripts', 'token'],
        ['transcripts', 'default_transcripts', 'token'],
        ['transcripts', 'default_transcripts'],
    ]

    @data(*zip(backends, expected_trans_fields, expected_3pm_fields))
    @unpack
    def test_transcripts_fields(self, backend, expected_trans_fields, expected_3pm_fields):
        """
        Test xBlock's transcript fields list is correct.
        """
        player = self.player[backend](self.xblock)
        self.assertListEqual(player.trans_fields, expected_trans_fields)
        self.assertListEqual(player.three_pm_fields, expected_3pm_fields)

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
                self.assertIn(_('Not all the languages of transcripts fetched from video platform'), ex.detail)

    media_ids = [
        '44zaxzFsthY', '45263567468485', 'HRrr784kH8932Z', '202889234',
        'https://example.com/sample.mp4'
    ]
    media_urls = [
        [  # Youtube
            'https://www.youtube.com/watch?v=44zaxzFsthY'
        ],
        [  # Brightcove
            'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
            'https://studio.brightcove.com/products/videos/45263567468485',
        ],
        [  # Wistia
            'https://wi.st/medias/HRrr784kH8932Z'
        ],
        [  # Vimeo
            'https://vimeo.com/202889234'
        ],
        [  # Html5
            'https://example.com/sample.mp4'
        ],
    ]

    @data(*zip(backends, media_urls, media_ids))
    @unpack
    def test_media_id(self, backend, urls, expected_media_id):
        """
        Check that media id is extracted from the video url for {0} backend
        """
        for url in urls:
            player = self.player[backend](self.xblock)
            res = player.media_id(url)
            self.assertEqual(res, expected_media_id)

    @data(*zip(backends, media_urls))
    @unpack
    def test_match(self, backend, urls):
        """
        Check if provided video `href` validates in right way for {0} backend
        """
        for url in urls:
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
                error = ex.detail
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
                message = ex.detail
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
                self.assertIsInstance(res, str)
                self.assertEqual(res, expected_default_transcript)
            except VideoXBlockException as ex:
                message = ex.detail
            except etree.XMLSyntaxError:
                message = 'XMLSyntaxError exception'
            expected_message = mock.expected_value[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()

    download_video_url_delegates = [
        'download_video_url',
        'download_video_url',
        'download_video_url',
        'download_video_url',
        'href',
    ]

    @data(*zip(backends, download_video_url_delegates))
    @unpack
    def test_download_video_url_delegates_to_proper_xblock_attribute(self, backend, patch_target):
        """
        Test video downloading URL delegates to proper xBlock's attribute.
        """
        # Arrange
        delegate_mock = PropertyMock()
        setattr(self.xblock, patch_target, delegate_mock)
        player = self.player[backend](self.xblock)

        # Act
        download_video_url = player.download_video_url

        # Assert
        self.assertEqual(download_video_url, delegate_mock)


class VimeoApiClientTest(VideoXBlockTestBase):
    """
    Test Vimeo backend API client.
    """

    def setUp(self):
        super(VimeoApiClientTest, self).setUp()
        self.vimeo_api_client = vimeo.VimeoApiClient(token='test_token')
        self.vimeo_player = vimeo.VimeoPlayer(self.xblock)

    @patch('video_xblock.backends.vimeo.requests.get')
    def test_api_client_get_200(self, requests_get_mock):
        """
        Test Vimeo's API client GET method if status Ok returned.
        """
        # Arrange
        test_body = {'test': 'body'}
        requests_get_mock.return_value = ResponseStub(status_code=200, body=test_body)

        # Act
        response = self.vimeo_api_client.get(url='test_url')

        # Assert
        requests_get_mock.assert_called_with('test_url', headers={
            'Accept': 'application/json',
            'Authorization': 'Bearer test_token'
        })
        self.assertEqual(response, test_body)

    @patch('video_xblock.backends.vimeo.requests.get')
    def test_api_client_get_400(self, requests_get_mock):
        """
        Test Vimeo's API client GET method if status 400 returned.
        """
        # Arrange
        requests_get_mock.return_value = ResponseStub(status_code=400)

        # Act & Assert
        self.assertRaises(vimeo.VimeoApiClientError, self.vimeo_api_client.get, url='test_url')

    def test_api_client_post(self):
        """
        Test Vimeo's API client POST method.
        """
        self.assertRaises(vimeo.VimeoApiClientError, self.vimeo_api_client.post, "test_url", "test_payload")

    @patch('video_xblock.backends.vimeo.VimeoPlayer.get_transcript_language_parameters')
    def test_parse_vimeo_texttracks(self, get_lang_params_mock):
        """
        Test Vimeo's texttracks API parsing utility with correct data.
        """
        # Arrange
        transcripts_data = [{
            'hls_link_expires_time': 1498128010,
            'name': 'English_captions_video.vtt',
            'language': 'en',
            'uri': '/texttracks/1234567',
            'link_expires_time': 1498128010,
            'hls_link': 'test_hls_captions_url',
            'link': 'test_captions_url',
            'active': True,
            'type': 'subtitles'
        }]
        get_lang_params_mock.return_value = ('en', 'English')

        # Act
        parsed = self.vimeo_player.parse_vimeo_texttracks(transcripts_data)

        # Assert
        self.assertEqual(parsed, [{
            'lang': transcripts_data[0]['language'],
            'label': 'English',
            'url': transcripts_data[0]['link']
        }])

    @patch('video_xblock.backends.vimeo.VimeoPlayer.get_transcript_language_parameters')
    def test_parse_vimeo_texttracks_empty_data(self, get_lang_params_mock):
        """
        Test Vimeo's texttracks API parsing utility with empty data.
        """
        # Arrange
        transcripts_data = [{}]
        get_lang_params_mock.return_value = ('en', 'English')

        # Act & Assert
        self.assertRaises(vimeo.VimeoApiClientError, self.vimeo_player.parse_vimeo_texttracks, transcripts_data)

    def test_vimeo_get_default_transcripts(self):
        """
        Test Vimeo's default transcripts fetching (positive scenario).
        """
        # Arrange
        test_json_data = {"data": [{"test_key": "test_value"}]}
        success_message = _('Default transcripts successfully fetched from a video platform.')

        with patch.object(self.vimeo_player, 'api_client') as api_client_mock, \
                patch.object(self.vimeo_player, 'parse_vimeo_texttracks') as parse_texttracks_mock:
            type(api_client_mock).access_token = PropertyMock(return_value="test_token")
            api_client_mock.get.return_value = test_json_data
            parse_texttracks_mock.return_value = test_json_data["data"]

            # Act
            transcripts, message = self.vimeo_player.get_default_transcripts(video_id="test_video_id")

            # Assert
            api_client_mock.get.assert_called_with('https://api.vimeo.com/videos/test_video_id/texttracks')
            parse_texttracks_mock.assert_called_with(test_json_data["data"])

            self.assertIsInstance(transcripts, list)
            self.assertEqual(message, success_message)

    def test_vimeo_get_default_transcripts_no_token(self):
        """
        Test Vimeo's default transcripts fetching without provided API token.
        """
        # Arrange
        failure_message = _('No API credentials provided.')

        with patch.object(self.vimeo_player, 'api_client') as api_client_mock:
            type(api_client_mock).access_token = PropertyMock(return_value=None)

            # Act
            with self.assertRaises(vimeo.VimeoApiClientError) as raised:
                self.vimeo_player.get_default_transcripts()

                # Assert
                self.assertEqual(str(raised.exception), failure_message)

    def test_vimeo_get_default_transcripts_get_failed(self):
        """
        Test Vimeo's default transcripts fetching with GET request failure.
        """
        # Arrange
        failure_message = _('No timed transcript may be fetched from a video platform.<br>')

        with patch.object(self.vimeo_player, 'api_client') as api_client_mock:
            type(api_client_mock).access_token = PropertyMock(return_value="test_token")
            api_client_mock.get.side_effect = vimeo.VimeoApiClientError()

            # Act
            default_transcripts, message = self.vimeo_player.get_default_transcripts(video_id="test_video_id")

            # Assert
            self.assertEqual(default_transcripts, [])
            self.assertEqual(message, failure_message)

    def test_vimeo_get_default_transcripts_no_data(self):
        """
        Test Vimeo's default transcripts fetching with no data returned.
        """
        # Arrange
        test_json_data = []
        success_message = _('There are no default transcripts for the video on the video platform.')

        with patch.object(self.vimeo_player, 'api_client') as api_client_mock:
            type(api_client_mock).access_token = PropertyMock(return_value="test_token")
            api_client_mock.get.return_value = test_json_data

            # Act
            transcripts, message = self.vimeo_player.get_default_transcripts(video_id="test_video_id")

            # Assert
            self.assertEqual(transcripts, [])
            self.assertEqual(message, success_message)

    def test_vimeo_get_default_transcripts_parsing_failure(self):
        """
        Test Vimeo's default transcripts fetching with data parsing failure.
        """
        # Arrange
        test_json_data = {"data": [{"test_key": "test_value"}]}
        failure_message = "test_message"

        with patch.object(self.vimeo_player, 'api_client') as api_client_mock, \
                patch.object(self.vimeo_player, 'parse_vimeo_texttracks') as parse_texttracks_mock:
            type(api_client_mock).access_token = PropertyMock(return_value="test_token")
            api_client_mock.get.return_value = test_json_data
            parse_texttracks_mock.side_effect = vimeo.VimeoApiClientError(failure_message)

            # Act
            transcripts, message = self.vimeo_player.get_default_transcripts(video_id="test_video_id")

            # Assert
            self.assertEqual(transcripts, [])
            self.assertEqual(message, failure_message)

    @patch('video_xblock.backends.vimeo.remove_escaping')
    @patch('video_xblock.backends.vimeo.requests.get')
    def test_vimeo_download_default_transcript(self, requests_get_mock, unescape_mock):
        """
        Test Vimeo's default transcripts downloading.
        """
        # Arrange
        test_file_data = u"test_file_data"
        requests_get_mock.return_value = Mock(content=test_file_data)

        # Act
        self.vimeo_player.download_default_transcript(url='test_url')

        # Assert
        requests_get_mock.assert_called_once_with('test_url')
        self.assertTrue(unescape_mock.called)


class WistiaPlayerTest(VideoXBlockTestBase):
    """
    Test Wistia backend player functionality.
    """

    def setUp(self):
        super(WistiaPlayerTest, self).setUp()
        self.wistia_player = wistia.WistiaPlayer(self.xblock)

    @patch('video_xblock.backends.wistia.babelfish.Language')
    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_success(self, requests_get_mock, babel_mock):
        """
        Test Wistia's default transcripts fetching (positive scenario).
        """
        # Arrange
        # ref: https://wistia.com/doc/data-api#captions_index
        test_api_data = [{'language': 'eng', 'english_name': 'English', }]
        requests_get_mock.return_value = ResponseStub(status_code=200, body=test_api_data)
        babel_mock.return_value = lang_mock = Mock()
        type(lang_mock).alpha2 = PropertyMock(return_value="en")
        kwargs = {
            'video_id': 'test_video_id',
            'token': 'test_token'
        }
        test_url = 'https://api.wistia.com/v1/medias/test_video_id/captions.json?api_password=test_token'
        test_download_url = 'http://api.wistia.com/v1/medias/test_video_id/captions/eng.json?api_password=test_token'
        test_message = _('Success.')
        test_transcripts = [{
            'lang': 'en',
            'label': 'English',
            'url': test_download_url,
            'source': TranscriptSource.DEFAULT
        }]

        with patch.object(self.wistia_player, 'get_transcript_language_parameters') as get_params_mock:
            get_params_mock.return_value = ('en', 'English')

            # Act
            transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

            # Assert
            requests_get_mock.assert_called_once_with(test_url)
            self.assertEqual(transcripts, test_transcripts)
            self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_api_failure(self, requests_get_mock):
        """
        Test Wistia's default transcripts fetching (request failure).
        """
        # Arrange
        kwargs = {
            'video_id': 'test_video_id',
            'token': 'test_token'
        }
        test_message = _('No timed transcript may be fetched from a video platform.\nError details: test_exc_message')
        test_url = 'https://api.wistia.com/v1/medias/test_video_id/captions.json?api_password=test_token'
        requests_get_mock.side_effect = requests.RequestException("test_exc_message")

        # Act
        transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

        # Assert
        requests_get_mock.assert_called_once_with(test_url)
        self.assertEqual(transcripts, [])
        self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_wrong_video(self, requests_get_mock):
        """
        Test Wistia's default transcripts fetching (not found case).
        """
        # Arrange
        kwargs = {
            'video_id': 'test_wrong_video_id',
            'token': 'test_token'
        }
        test_message = "Wistia video test_wrong_video_id doesn't exist."
        test_url = 'https://api.wistia.com/v1/medias/test_wrong_video_id/captions.json?api_password=test_token'
        requests_get_mock.return_value = ResponseStub(status_code=404, body=[])

        # Act
        transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

        # Assert
        requests_get_mock.assert_called_once_with(test_url)
        self.assertEqual(transcripts, [])
        self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_bad_request_or_else(self, requests_get_mock):
        """
        Test Wistia's default transcripts fetching (request.ok == False).
        """
        # Arrange
        kwargs = {
            'video_id': 'test_video_id',
            'token': 'test_token'
        }
        test_message = "Invalid request."
        test_url = 'https://api.wistia.com/v1/medias/test_video_id/captions.json?api_password=test_token'
        requests_get_mock.return_value = ResponseStub(status_code=400, ok=False, body=[])

        # Act
        transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

        # Assert
        requests_get_mock.assert_called_once_with(test_url)
        self.assertEqual(transcripts, [])
        self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_bad_json(self, requests_get_mock):
        """
        Test Wistia's default transcripts fetching (can't parse response JSON).
        """
        # Arrange
        kwargs = {
            'video_id': 'test_video_id',
            'token': 'test_token'
        }
        test_message = "For now, video platform doesn't have any timed transcript for this video."
        test_url = 'https://api.wistia.com/v1/medias/test_video_id/captions.json?api_password=test_token'
        requests_get_mock.return_value = response_mock = ResponseStub(status_code=200)
        response_mock.json = Mock(side_effect=ValueError())

        # Act
        transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

        # Assert
        requests_get_mock.assert_called_once_with(test_url)
        self.assertEqual(transcripts, [])
        self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.babelfish.Language')
    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_get_default_transcripts_baberlfish(self, requests_get_mock, babel_mock):
        """
        Test Wistia's default transcripts fetching (babelfish fallback).
        """
        # Arrange
        # ref: https://wistia.com/doc/data-api#captions_index
        test_api_data = [{'language': 'eng', 'english_name': 'English', }]
        requests_get_mock.return_value = ResponseStub(status_code=200, body=test_api_data)
        babel_mock.return_value = lang_code_mock = Mock()
        type(lang_code_mock).alpha2 = PropertyMock(side_effect=ValueError())

        kwargs = {
            'video_id': 'test_video_id',
            'token': 'test_token'
        }
        test_url = 'https://api.wistia.com/v1/medias/test_video_id/captions.json?api_password=test_token'
        test_download_url = 'http://api.wistia.com/v1/medias/test_video_id/captions/eng.json?api_password=test_token'
        test_message = _('Success.')
        test_transcripts = [{
            'lang': babel_mock.fromalpha3b().alpha2,
            'label': 'English',
            'url': test_download_url,
            'source': TranscriptSource.DEFAULT
        }]

        with patch.object(self.wistia_player, 'get_transcript_language_parameters') as get_params_mock:
            get_params_mock.return_value = ('en', 'English')

            # Act
            transcripts, message = self.wistia_player.get_default_transcripts(**kwargs)

            # Assert
            requests_get_mock.assert_called_once_with(test_url)
            self.assertEqual(transcripts, test_transcripts)
            self.assertEqual(message, test_message)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_download_default_transcript_success(self, requests_get_mock):
        """
        Test Wistia's default transcripts downloading (positive scenario).
        """
        # Arrange
        test_api_data = {'text': 'test_content'}
        test_url = "test_url"
        test_language_code = "test_language_code"

        requests_get_mock.return_value = ResponseStub(status_code=200, body=test_api_data)

        # Act
        content = self.wistia_player.download_default_transcript(test_url, test_language_code)

        # Assert
        self.assertEqual(content, 'test_content')
        requests_get_mock.assert_called_once_with(test_url)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_download_default_transcript_api_failure(self, requests_get_mock):
        """
        Test Wistia's default transcripts downloading (request failure).
        """
        # Arrange
        test_url = u"test_url"
        test_language_code = u"test_language_code"

        requests_get_mock.side_effect = requests.RequestException()

        # Act
        content = self.wistia_player.download_default_transcript(test_url, test_language_code)

        # Assert
        self.assertEqual(content, '')
        requests_get_mock.assert_called_once_with(test_url)

    @patch('video_xblock.backends.wistia.requests.get')
    def test_wistia_download_default_transcript_parsing_failure(self, requests_get_mock):
        """
        Test Wistia's default transcripts downloading (request parsing failure).
        """
        # Arrange
        test_url = "test_url"
        test_language_code = u"test_language_code"

        requests_get_mock.return_value = []     # has no 'text' attribute

        # Act
        content = self.wistia_player.download_default_transcript(test_url, test_language_code)

        # Assert
        self.assertEqual(content, '')
        requests_get_mock.assert_called_once_with(test_url)


class BrightcovePlayerTest(VideoXBlockTestBase):
    """
    Test Brightcove backend.
    """

    def setUp(self):
        super(BrightcovePlayerTest, self).setUp()
        self.bc_player = brightcove.BrightcovePlayer(self.xblock)

    @patch('video_xblock.backends.brightcove.requests.get')
    def test_brightcove_get_default_transcripts_no_text(self, requests_get_mock):
        """
        Test Brightcove's default transcripts fetching (empty text fetched).
        """
        # Arrange
        self.bc_player.api_key = 'test_api_key'
        self.bc_player.api_secret = 'test_api_secret'
        kwargs = {
            'account_id': 'test_account_id',
            'video_id': 'test_video_id'
        }
        test_message = "No timed transcript may be fetched from a video platform."
        test_url = 'https://cms.api.brightcove.com/v1/accounts/test_account_id/videos/test_video_id'
        test_headers = {'Authorization': 'Bearer None'}
        requests_get_mock.return_value = ResponseStub(status_code=200, body='')

        # Act
        transcripts, message = self.bc_player.get_default_transcripts(**kwargs)

        # Assert
        requests_get_mock.assert_called_once_with(test_url, headers=test_headers)
        self.assertEqual(transcripts, [])
        self.assertEqual(message, test_message)

    @patch('video_xblock.backends.brightcove.BrightcoveApiClient.create_credentials')
    def test_brightcove_authenticate_api(self, api_client_create_creds_mock):
        """
        Test Brightcove's api authentication (not CREATED or no response data).
        """
        # Arrange
        kwargs = {
            'token': 'test_token',
            'account_id': '1'
        }
        test_message = "test_message"
        api_client_create_creds_mock.side_effect = brightcove.BrightcoveApiClientError("test_message")

        # Act
        auth_data, error_message = self.bc_player.authenticate_api(**kwargs)

        # Assert
        self.assertEqual(auth_data, {})
        self.assertEqual(error_message, test_message)
