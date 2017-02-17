describe('Player state', function() {
    'use strict';
    var playerId = 'test_id';
    var player = {
        captionsLanguage: 'en'
    };
    window.videoPlayerId = playerId;
    beforeEach(function() {
        var video = document.createElement('video');
        video.id = playerId;
        video.className = 'video-js vjs-default-skin';
        document.body.appendChild(video);
    });
    it('return download transcript url', function() {
        // TODO avoid the eslint shutdown for the implicity got variables
        expect(getDownloadTranscriptUrl(player)).toBe(transcripts.en.url); // eslint-disable-line
    });
});
