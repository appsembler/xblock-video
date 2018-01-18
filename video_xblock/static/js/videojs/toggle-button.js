/**
 * The initial caption and transcript button.
 * Add "ToggleButton" to Video.js as plugin.
 */

domReady(function() {
    'use strict';
    // Videojs 5/6 shim;
    var registerPlugin = videojs.registerPlugin || videojs.plugin;

    var MenuItem = videojs.getComponent('MenuItem');
   /**
    *  Custom Video.js component responsible for creation of the menu with custom captions/transcripts buttons.
    */
    var ToggleMenuItem = videojs.extend(MenuItem, {
        constructor: function constructor(player, options) {
            MenuItem.call(this, player, options);
            this.on('click', this.onClick);
            this.createEl();
        },
        enabledEventName: function enabledEventName() {
            return this.options_.enabledEvent;
        },
        disabledEventName: function disabledEventName() {
            return this.options_.disabledEvent;
        },
        createEl: function createEl(type, props, attributes) {
            var menuProps = props || {};
            var el = MenuItem.prototype.createEl.call(this, arguments.tag, menuProps, attributes);
            el.setAttribute('role', 'menuitem');
            el.setAttribute('aria-live', 'polite');
            el.setAttribute('data-lang', this.options_.track.language);
            return el;
        },
        onClick: function onClick(event) {
            var menuItem = this.$$('.vjs-menu-item', this.el_.parentNode);
            var el = event.currentTarget;
            var self = this;
            var tracks = this.player_.textTracks();
            Array.from(menuItem).forEach(function(caption) {
                caption.classList.remove('vjs-selected');
            });
            el.classList.add('vjs-selected');

            tracks.tracks_.forEach(function(track) {
                if (track.kind === 'captions') {
                    self.player_.captionsLanguage = el.dataset.lang;
                    if (track.language === self.player_.captionsLanguage) {
                        track.mode = 'showing';  // eslint-disable-line no-param-reassign
                    } else {
                        track.mode = 'disabled';  // eslint-disable-line no-param-reassign
                    }
                }
            });
            this.player_.trigger('captionstrackchange');
            this.player_.trigger('subtitlestrackchange');
            this.player_.trigger('languagechange');
        }
    });

    var MenuButton = videojs.getComponent('MenuButton');

   /**
    *  Custom Video.js component responsible for creation of the custom captions/transcripts buttons.
    */
    var ToggleButton = videojs.extend(MenuButton, {
        // base class for create buttons for caption and transcripts
        constructor: function constructor(player, options) {
            this.kind_ = 'captions';

            MenuButton.call(this, player, options);

            if (!this.player_.singleton_menu) {
                this.update();
                this.player_.singleton_menu = this.menu;
            } else {
                this.menu = this.player_.singleton_menu;
            }
            this.el_.setAttribute('aria-haspopup', 'true');
            this.el_.setAttribute('role', 'menuitem');

            // This variable is used by Video.js library
            this.enabled_ = true;  // eslint-disable-line no-underscore-dangle
            // Events of ToggleButton
            this.on('click', this.onClick);
            this.on('mouseenter', function() {
                var caretButton = this.$$('.vjs-custom-caret-button', this.el_.parentNode);
                if (caretButton.length > 0) {
                    caretButton[0].classList.add('fa-caret-up');
                    caretButton[0].classList.remove('fa-caret-left');
                }
            });
            this.on('mouseleave', function() {
                var caretButton = this.$$('.vjs-custom-caret-button', this.el_.parentNode);
                this.menu.el_.classList.remove('is-visible');
                if (caretButton.length > 0) {
                    caretButton[0].classList.remove('fa-caret-up');
                    caretButton[0].classList.add('fa-caret-left');
                }
            });

            this.createEl();
        },
        createItems: function createItems() {
            var items = arguments.length <= 0 || arguments[0] === undefined ? [] : arguments[0];
            var self = this;
            var tracks = this.player_.textTracks();
            if (!tracks) {
                return items;
            }
            tracks.tracks_.forEach(function(track) {  // eslint-disable-line no-param-reassign
                // only add tracks that are of the appropriate kind and have a label
                if (track.kind === self.kind_) {
                    items.push(new ToggleMenuItem(self.player_, {
                        // MenuItem is selectable
                        track: track,
                        label: track.label,
                        enabledEvent: self.enabledEventName(),
                        disabledEvent: self.disabledEventName()
                    }));
                }
            });
            return items;
        },
        styledSpan: function styledSpan() {
            return this.options_.style;
        },
        enabledEventName: function enabledEventName() {
            return this.options_.enabledEvent;
        },
        disabledEventName: function disabledEventName() {
            return this.options_.disabledEvent;
        },
        buildCSSClass: function buildCSSClass() {
            return this.options_.cssClasses;
        },
        createEl: function createEl(props, attributes) {
            var el;
            var menuProps = props || {};
            menuProps.className = this.buildCSSClass() + ' icon fa ' + this.styledSpan();
            menuProps.tabIndex = 0;

            el = MenuButton.prototype.createEl.call(this, arguments.tag, menuProps, attributes);
            el.setAttribute('role', 'menuitem');
            el.setAttribute('aria-live', 'polite');
            el.tabIndex = this.options_.tabIndex || 0;
            el.classList.add('icon');
            el.classList.add('fa');
            el.classList.add(this.styledSpan());
            el.classList.add('vjs-singleton');
            return el;
        },
        onClick: function onClick(event) {
            var el = event.currentTarget;
            var menusCollection = this.player_.el_.getElementsByClassName('vjs-lock-showing');
            var eventName = this.hasClass('vjs-control-enabled') ? this.disabledEventName() : this.enabledEventName();
            el.classList.toggle('vjs-control-enabled');
            this.player_.trigger(eventName);

            // kind a hack here - removing vjs special class to make lang menu appear on hover...
            for (var i = 0; i < menusCollection.length; i++) {  // eslint-disable-line vars-on-top
                menusCollection.item(i).classList.remove('vjs-lock-showing');
            }
            el.blur();
        }
    });

    var toggleButton = function(options) {
        this.controlBar.addChild('ToggleButton', options);
    };

    videojs.registerComponent('ToggleButton', ToggleButton);
    registerPlugin('toggleButton', toggleButton);
});
