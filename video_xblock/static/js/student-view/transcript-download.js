/**
 * This part is responsible for downloading of transcripts and captions in LMS and CMS.
 */

var TranscriptDownload = function(player) {
    'use strict';
    /** Send message of changing transcript to parent window */
    var transcripts = window.playerStateObj.transcriptsObject;
    var sendMessage = function() {
        var playerObj = this;
        parent.postMessage({
            action: 'downloadTranscriptChanged',
            downloadTranscriptUrl: getDownloadTranscriptUrl(transcripts, playerObj),
            xblockUsageId: getXblockUsageId()
        }, document.location.protocol + '//' + document.location.host);
    };

    if (!transcripts[player.captionsLanguage]) {
        player.captionsEnabled = player.transcriptsEnabled = false; // eslint-disable-line no-param-reassign
        // Need to trigger two events to disable active buttons in control bar
        player.trigger('transcriptdisabled');
        player.trigger('captiondisabled');
    }

    player.on('captionstrackchange', sendMessage);
};

domReady(function() {
    'use strict';
    videojs(window.videoPlayerId).ready(function() {
        TranscriptDownload(this);
    });
});
