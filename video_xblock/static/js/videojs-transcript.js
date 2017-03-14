/**
 * This part is responsible for creation of captions and transcripts buttons on player load.
 */
domReady(function() {
    'use strict';

    videojs(window.videoPlayerId).ready(function() {
        var enableTrack = false;
        var player_ = this;
        var cssClasses = 'vjs-custom-caption-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        // attach the widget to the page
        var transcriptContainer = document.getElementById('transcript');
        var captionContainer = document.getElementsByClassName('vjs-text-track-display');
        /** This function is wrapper for initial Brightcove's captions. */
        var initCaptions = function initCaptions() {
            var transcript;
            var tracks = player_.textTracks().tracks_;
            tracks.forEach(function(track) {
                if (track.kind === 'captions') {
                    if (track.language === player_.captionsLanguage) {
                        track.mode = 'showing';  // eslint-disable-line no-param-reassign
                        enableTrack = true;
                    } else {
                        track.mode = 'disabled';  // eslint-disable-line no-param-reassign
                    }
                }
            });
            if (!enableTrack && tracks[0].kind === 'captions') {
                tracks[0].mode = 'showing';
            }
            // fire up the plugin
            transcript = player_.transcript({
                showTrackSelector: false,
                showTitle: false,
                followPlayerTrack: true,
                tabIndex: 10
            });
            transcript.el().addEventListener('click', function() {
                player_.trigger('transcriptstatechanged');
            });

            // Show or hide the transcripts block depending on the transcript state
            if (!player_.transcriptsEnabled) {
                transcriptContainer.className += ' is-hidden';
            }
            transcriptContainer.appendChild(transcript.el());
        };

        if (this.tagAttributes.brightcove !== undefined) {
            // This branch for brightcove player
            this.one('loadedmetadata', initCaptions);
        } else {
            initCaptions();
        }

        this.on('transcriptenabled', function() {
            transcriptContainer.classList.remove('is-hidden');
            this.transcriptsEnabled = true;
            this.trigger('transcriptstatechanged');
        });
        this.on('transcriptdisabled', function() {
            transcriptContainer.classList.add('is-hidden');
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
            cssClasses: cssClasses,
            tabIndex: 6
        });
        cssClasses = 'vjs-custom-transcript-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        if (this.transcriptsEnabled) {
            cssClasses += ' vjs-control-enabled';
        }
        this.toggleButton({
            style: 'fa-quote-left',
            enabledEvent: 'transcriptenabled',
            disabledEvent: 'transcriptdisabled',
            cssClasses: cssClasses,
            tabIndex: 7
        });
        this.toggleButton({
            style: 'fa-caret-left',
            enabledEvent: 'caretenabled',
            disabledEvent: 'caretdisabled',
            cssClasses: 'vjs-custom-caret-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button',
            tabIndex: 8
        });
    });
});
