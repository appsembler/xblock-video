/* global getHandlers */

/**
 * Tests for studio edit's utils
 */
describe('Runtime handlers', function() {
    'use strict';

    var handlersMap = {
        downloadTranscript: 'download_transcript',
        authenticateVideoApi: 'authenticate_video_api_handler',
        uploadDefaultTranscript: 'upload_default_transcript_handler',
        validateThreePlayMediaConfig: 'validate_three_play_media_config',
        saveState: 'save_player_state',
        publishEvent: 'publish_event'
    };
    var runtimeMock = {
        handlerUrl: function(el, handlerName) {
            return handlerName;
        }
    };

    it('returns expected handlers', function() {
        expect(getHandlers(runtimeMock, 'element'))
            .toEqual(handlersMap);
    });
});
