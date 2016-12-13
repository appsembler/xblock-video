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
(function () {

    "use strict";
    function XBlockEventPlugin(options) {

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

        this.onReady = function () {
            this.log('ready_video');
        };

        this.onPlay = function () {
            this.log('play_video', {currentTime: this.currentTime()});
        };

        this.onPause = function () {
            this.log('pause_video', {currentTime: this.currentTime()});
        };

        this.onEnded = function () {
            this.log('stop_video', {currentTime: this.currentTime()});
        };

        this.onSkip = function (event, doNotShowAgain) {
            var info = {currentTime: this.currentTime()},
                eventName = doNotShowAgain ? 'do_not_show_again_video' : 'skip_video';
            this.log(eventName, info);
        };

        this.onSeek = function () {
            this.log('seek_video', {
                previous_time: previousTime,
                new_time: currentTime
            });
        };

        this.onSpeedChange = function (event, newSpeed, oldSpeed) {
            this.log('speed_change_video', {
                current_time: this.currentTime(),
                old_speed: oldSpeed,
                new_speed: newSpeed
            });
        };

        this.onShowLanguageMenu = function () {
            this.log('language_menu.shown');
        };

        this.onHideLanguageMenu = function () {
            this.log('language_menu.hidden', {language: this.language});
        };

        this.onShowTranscript = function () {
            this.log('show_transcript', {current_time: this.currentTime()});
        };

        this.onHideTranscript = function () {
            this.log('hide_transcript', {current_time: this.currentTime()});
        };

        this.onShowCaptions = function () {
            this.log('closed_captions.shown', {current_time: this.currentTime()});
        };

        this.onHideCaptions = function () {
            this.log('closed_captions.hidden', {current_time: this.currentTime()});
        };

        this.logEvent = function (event_type) {
            if (this.events.indexOf(event_type) == -1 || typeof this[event_type] !== 'function') {
                return;
            }
            this[event_type]();
        };

        this.ready(function () {
            this.logEvent('onReady')
        })
            .on('timeupdate', function () {
                previousTime = currentTime;
                currentTime = this.currentTime();
            })
            .on('ratechange', function () {
                this.logEvent('onSpeedChange')
            })
            .on('play', function () {
                this.logEvent('onPlay')
            })
            .on('pause', function () {
                this.logEvent('onPause')
            })
            .on('ended', function () {
                this.logEvent('onEnded')
            })
            .on('seeked', function () {
                this.logEvent('onSeek')
            });

        /* TODO Catch events bellow after theirs implementation
         onShowLanguageMenu, onHideLanguageMenu, onShowTranscript, onHideTranscript, onShowCaptions, onHideCaptions
         */
        this.log = function (eventName, data) {
            data = data || {};
            data['eventType'] = 'xblock-video.' + eventName;
            parent.postMessage({
                'action': 'analytics',
                'event_data': data,
                'xblockUsageId': xblockUsageId
            }, document.origin);
        };

        return this;

    }

    window.xblockEventPlugin = XBlockEventPlugin;
    window.videojs.plugin('xblockEventPlugin', xblockEventPlugin);

}).call(this);
