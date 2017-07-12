/**
 * Runtime handlers factory.
 *
 * Returns an object with all XBlock runtime handlers required by Video Xblock.
 */
function getHandlers(runtime, element) {
    'use strict';
    return {
        downloadTranscript: runtime.handlerUrl(element, 'download_transcript'),
        authenticateVideoApi: runtime.handlerUrl(element, 'authenticate_video_api_handler'),
        uploadDefaultTranscript: runtime.handlerUrl(element, 'upload_default_transcript_handler'),
        validateThreePlayMediaConfig: runtime.handlerUrl(element, 'validate_three_play_media_config'),
        saveState: runtime.handlerUrl(element, 'save_player_state'),
        publishEvent: runtime.handlerUrl(element, 'publish_event')
    };
}
