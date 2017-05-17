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
        getTranscripts3playmediaApi: runtime.handlerUrl(element, 'get_transcripts_3playmedia_api_handler'),
        saveState: runtime.handlerUrl(element, 'save_player_state'),
        publishEvent: runtime.handlerUrl(element, 'publish_event')
    };
}
