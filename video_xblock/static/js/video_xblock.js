
/** Javascript for VideoXBlock.student_view() */
function VideoXBlockStudentViewInit(runtime, element) {
    'use strict';
    var stateHandlerUrl = runtime.handlerUrl(element, 'save_player_state');
    var eventHandlerUrl = runtime.handlerUrl(element, 'publish_event');
    var downloadTranscriptHandlerUrl = runtime.handlerUrl(element, 'download_transcript');
    var usageId = element.attributes['data-usage-id'].value;
    window.videoXBlockState = window.videoXBlockState || {};
    var handlers = window.videoXBlockState.handlers =  // eslint-disable-line vars-on-top
        window.videoXBlockState.handlers || {
            saveState: {},
            analytics: {}
        };
    handlers.saveState[usageId] = stateHandlerUrl;
    handlers.analytics[usageId] = eventHandlerUrl;
    /** Send data to server by POSTing it to appropriate VideoXBlock handler */
    function sendData(handlerUrl, data) {
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data)
        })
        .done(function() {
            console.log('Data processed successfully.');  // eslint-disable-line no-console
        })
        .fail(function() {
            console.log('Failed to process data');  // eslint-disable-line no-console
        });
    }
    if (!window.videoXBlockListenerRegistered) {
        // Make sure we register event listener only once even if there are more than
        // one VideoXBlock on a page
        window.addEventListener('message', receiveMessage, false);  // eslint-disable-line no-use-before-define
        window.videoXBlockListenerRegistered = true;
    }
    /**
        * Receive a message from child frames.
        * Expects a specific type of messages containing video player state to be saved on a server.
        * Pass the sate to `saveState()` for handling.
    */
    function receiveMessage(event) {
        // For Chrome, the origin property is in the event.originalEvent object.
        var origin = event.origin || event.originalEvent.origin;
        if (origin !== document.location.protocol + '//' + document.location.host) {
            // Discard a message received from another domain
            return;
        }
        try {
            if (event.data.action === 'downloadTranscriptChanged') {
                // eslint-disable-next-line no-use-before-define
                updateTranscriptDownloadUrl(event.data.downloadTranscriptUrl);
            }
            var url = handlers[event.data.action][event.data.xblockUsageId];  // eslint-disable-line vars-on-top
            if (url) {
                sendData(url, event.data.info);
            }
        } catch (err) {
            console.log(err);  // eslint-disable-line no-console
        }
    }
    /** Updates transcript download url if it is enabled */
    function updateTranscriptDownloadUrl(downloadTranscriptUrl) {
        var downloadLinkEl = document.getElementById('download-transcript-button');
        var link;
        if (downloadLinkEl) {
            link = downloadLinkEl.getElementsByTagName('a')[0];
            if (downloadTranscriptUrl) {
                link.href = downloadTranscriptHandlerUrl + '?' + downloadTranscriptUrl;
                downloadLinkEl.classList.remove('is-hidden');
            } else {
                link.href = '#';
                downloadLinkEl.classList.add('is-hidden');
            }
        }
    }
}
