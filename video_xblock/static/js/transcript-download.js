domReady(function() {
    'use strict';
    videojs('{{ video_player_id }}').ready(function() {
        var player = this;
        var transcripts = JSON.parse('{{ player_state.transcripts_object }}');
        var xblockUsageId = window.location.hash.slice(1);
        /** Get transcript url for current caption language */
        var getDownloadTranscriptUrl = function() {
            var downloadTranscriptUrl;
            if (transcripts[player.captionsLanguage]) {
                downloadTranscriptUrl = transcripts[player.captionsLanguage].url;
            }
            return downloadTranscriptUrl;
        };
        var sendMessage = function() {
            parent.postMessage({
                action: 'downloadTranscriptChanged',
                downloadTranscriptUrl: getDownloadTranscriptUrl(),
                xblockUsageId: xblockUsageId
            }, document.location.protocol + '//' + document.location.host);
        };
        if (!transcripts[player.captionsLanguage]) {
            player.captionsEnabled = player.transcriptsEnabled = false;
            // Need to trigger two events to disable active buttons in control bar
            player.trigger('transcriptdisabled');
            player.trigger('captiondisabled');
        }
        player.on('changedownloadtranscripturl', sendMessage);
    });
});
