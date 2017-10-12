/**
 * This part is responsible for tracking video player events.
 * List of events:
 * - onReady
 * - onPlay
 * - onPause
 * - onEnded
 * - onSeek
 * - onSpeedChange
 *
 */
(function() {
    'use strict';
    /**
     * Videojs plugin.
     * Listens for events and send them to parent frame to be logged in Open edX tracking log
     * @param {Object} options - Plugin options passed in at initialization time.
     */
    function XBlockEventPlugin() {
        var player = this;
        var previousTime = 0;
        var currentTime = 0;

        this.events = [
            'onReady',
            'onPlay',
            'onPause',
            'onEnded',
            'onSpeedChange',
            'onSeek',
            'onShowLanguageMenu',
            'onHideLanguageMenu',
            'onShowTranscript',
            'onHideTranscript',
            'onShowCaptions',
            'onHideCaptions'
        ];

        this.onReady = function() {
            this.log('ready_video');
        };

        this.onPlay = function() {
            this.log('play_video', {currentTime: this.currentTime()});
        };

        this.onPause = function() {
            this.log('pause_video', {currentTime: this.currentTime()});
        };

        this.onEnded = function() {
            this.log('stop_video', {currentTime: this.currentTime()});
        };

        this.onSkip = function(event, doNotShowAgain) {
            var info = {currentTime: this.currentTime()},
                eventName = doNotShowAgain ? 'do_not_show_again_video' : 'skip_video';
            this.log(eventName, info);
        };

        this.onSeek = function() {
            this.log('seek_video', {
                previous_time: previousTime,
                new_time: currentTime
            });
        };

        this.onSpeedChange = function(event, newSpeed, oldSpeed) {
            this.log('speed_change_video', {
                current_time: this.currentTime(),
                old_speed: oldSpeed,
                new_speed: newSpeed
            });
        };

        this.onShowLanguageMenu = function() {
            this.log('language_menu.shown');
        };

        this.onHideLanguageMenu = function() {
            this.log('language_menu.hidden', {language: this.language});
        };

        this.onShowTranscript = function() {
            this.log('show_transcript', {current_time: this.currentTime()});
        };

        this.onHideTranscript = function() {
            this.log('hide_transcript', {current_time: this.currentTime()});
        };

        this.onShowCaptions = function() {
            this.log('closed_captions.shown', {current_time: this.currentTime()});
        };

        this.onHideCaptions = function() {
            this.log('closed_captions.hidden', {current_time: this.currentTime()});
        };
        this.logEvent = function(eventType) {
            if (this.events.indexOf(eventType) === -1 || typeof this[eventType] !== 'function') {
                return;
            }
            this[eventType]();
        };
        this.ready(function() {
            this.logEvent('onReady');
        });
        player.on('timeupdate', function() {
            previousTime = currentTime;
            currentTime = this.currentTime();
        });
        player.on('ratechange', function() {
            this.logEvent('onSpeedChange');
        });
        player.on('play', function() {
            this.logEvent('onPlay');
        });
        player.on('pause', function() {
            this.logEvent('onPause');
        });
        player.on('ended', function() {
            this.logEvent('onEnded');
        });
        player.on('seeked', function() {
            this.logEvent('onSeek');
        });

        /* TODO Add following events forwarding to Open edX when respective features are implemented
         onShowLanguageMenu, onHideLanguageMenu, onShowTranscript, onHideTranscript, onShowCaptions, onHideCaptions
         */
        this.log = function(eventName, data) {
            var xblockUsageId = getXblockUsageId();
            data = data || {};  //  eslint-disable-line no-param-reassign
            data.eventType = 'xblock-video.' + eventName;  //  eslint-disable-line no-param-reassign
            parent.postMessage({
                action: 'analytics',
                info: data,
                xblockUsageId: xblockUsageId
            }, document.location.protocol + '//' + document.location.host);
        };
        return this;
    }
    window.xblockEventPlugin = XBlockEventPlugin;
    // add plugin if player has already initialized
    if (window.videojs) {
        window.videojs.plugin('xblockEventPlugin', xblockEventPlugin);  // eslint-disable-line no-undef
    }
}).call(this);
