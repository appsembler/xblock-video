/**
 * The initial caption and transcript button.
 * Add "ToggleButton" to videojs as plugin.
 */

domReady(function() {
    'use strict';

    var MenuItem = videojs.getComponent('MenuItem');
    var ToggleMenuItem = videojs.extend(MenuItem, {
        // base class for create buttons for caption and transcripts
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
            var el = MenuItem.prototype.createEl.call(this, arguments.tag, props || {}, attributes);
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
    var ClickableComponent = videojs.getComponent('ClickableComponent');

    var ToggleButton = videojs.extend(MenuButton, {
        // base class for create buttons for caption and transcripts
        constructor: function constructor(player, options) {
            this.kind_ = 'captions';

            ClickableComponent.call(this, player, options);

            if (!this.player_.singleton_menu) {
                this.update();
                this.player_.singleton_menu = this.menu;
            } else {
                this.menu = this.player_.singleton_menu;
            }
            this.el_.setAttribute('aria-haspopup', 'true');
            this.el_.setAttribute('role', 'menuitem');

            // This variable uses in videojs library
            this.enabled_ = true;  // eslint-disable-line no-underscore-dangle
            // Events of ToggleButton
            this.on('click', this.onClick);
            this.on('mouseenter', function() {
                var caretButton = this.$$('.vjs-custom-caret-button', this.el_.parentNode);
                this.menu.el_.classList.add('is-visible');
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
            var el = MenuButton.prototype.createEl.call(this, arguments.tag, props || {}, attributes);
            props.className = this.buildCSSClass() +   // eslint-disable-line no-param-reassign
                ' icon fa ' + this.styledSpan();
            props.tabIndex = 0;  // eslint-disable-line no-param-reassign
            el.setAttribute('role', 'menuitem');
            el.setAttribute('aria-live', 'polite');
            el.classList += ' icon fa ' + this.styledSpan();
            el.classList.add('vjs-singleton');
            return el;
        },
        onClick: function onClick(event) {
            var el = event.currentTarget;
            var eventName = this.hasClass('vjs-control-enabled') ? this.enabledEventName() : this.disabledEventName();
            el.classList.toggle('vjs-control-enabled');
            this.player_.trigger(eventName);
        }
    });

    var toggleButton = function(options) {
        if (this.tagAttributes.brightcove !== undefined) {
            this.controlBar.customControlSpacer.addChild('ToggleButton', options);
        } else {
            this.controlBar.addChild('ToggleButton', options);
        }
    };

    videojs.registerComponent('ToggleButton', ToggleButton);
    videojs.plugin('toggleButton', toggleButton);
});
