domReady(function() {
    'use strict';
    videojs('{{ video_player_id }}').ready(function() {
        var tracks = this.textTracks();
        var enableTrack = false;
        var cssClasses = 'vjs-custom-caption-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        // fire up the plugin
        var transcript = this.transcript({
            showTrackSelector: false,
            showTitle: false,
            followPlayerTrack: true
        });
        // attach the widget to the page
        var transcriptContainer = document.getElementById('transcript');
        var captionContainer = document.getElementsByClassName('vjs-text-track-display');
        for (var i = 0; i < tracks.length; i++) {  //  eslint-disable-line vars-on-top
            var track = tracks[i];                 //  eslint-disable-line vars-on-top
            if (track.kind === 'captions') {
                if (track.language === this.captionsLanguage) {
                    track.mode = 'showing';
                    enableTrack = true;
                } else {
                    track.mode = 'disabled';
                }
                if (!enableTrack && i === tracks.length - 1) {
                    tracks[0].mode = 'showing';
                }
            }
        }
        // Show or hide the transcripts block depending on the transcript state
        if (!this.transcriptsEnabled) {
            transcriptContainer.className += ' is-hidden';
        }
        transcriptContainer.appendChild(transcript.el());

        this.on('transcriptenabled', function() {
            transcriptContainer.classList.toggle('is-hidden');
            this.transcriptsEnabled = true;
            this.trigger('transcriptstatechanged');
        });
        this.on('transcriptdisabled', function() {
            transcriptContainer.classList.toggle('is-hidden');
            this.transcriptsEnabled = false;
            this.trigger('transcriptstatechanged');
        });
        // Show or hide the captions block depending on the caption state
        if (!this.captionsEnabled) {
            Array.from(captionContainer).forEach(function(caption) {
                caption.className += ' is-hidden';  // eslint-disable-line no-param-reassign
            });
        }

        this.on('captionenabled', function() {
            Array.from(captionContainer).forEach(function(caption) {
                caption.classList.toggle('is-hidden', false);
            });
            this.captionsEnabled = true;
            this.trigger('captionstatechanged');
        });
        this.on('captiondisabled', function() {
            Array.from(captionContainer).forEach(function(caption) {
                caption.classList.toggle('is-hidden', true);
            });
            this.captionsEnabled = false;
            this.trigger('captionstatechanged');
        });
        if (this.captionsEnabled) {
            cssClasses += ' vjs-control-enabled';
        }
        this.toggleButton({
            style: 'fa-cc',
            enabledEvent: 'captionenabled',
            disabledEvent: 'captiondisabled',
            cssClasses: cssClasses
        });
        cssClasses = 'vjs-custom-transcript-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        if (this.transcriptsEnabled) {
            cssClasses += ' vjs-control-enabled';
        }
        this.toggleButton({
            style: 'fa-quote-left',
            enabledEvent: 'transcriptenabled',
            disabledEvent: 'transcriptdisabled',
            cssClasses: cssClasses
        });
    });
});
