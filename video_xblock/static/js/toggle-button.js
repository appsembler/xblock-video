/**
 * The initial caption and transcript button.
 * Add "ToggleButton" to videojs as plugin.
 */

domReady(function() {

  var MenuItem = videojs.getComponent('MenuItem');
  var ToggleMenuItem = videojs.extend(MenuItem, {
    // base class for create buttons for caption and transcripts
    constructor: function constructor(player, options) {
      MenuItem.call(this, player, options);
      this.on('click', this.onClick);
      this.createEl();
    },
    enabledEventName: function enabledEventName() {
      return this.options_['enabledEvent'];
    },
    disabledEventName: function disabledEventName() {
      return this.options_['disabledEvent'];
    },
    createEl: function createEl(type, props, attributes) {
      props = props || {};
      var el = MenuItem.prototype.createEl.call(this, arguments.tag, props, attributes);
      el.setAttribute('role', 'menuitem');
      el.setAttribute('aria-live', 'polite');
      el.setAttribute('data-lang', this.options_.track.language);
      return el;
    },
    onClick: function onClick(event) {
      var menuItem = this.$$('.vjs-menu-item', this.el_.parentNode);
      var el = event.currentTarget;
      Array.from(menuItem).forEach(function(caption) {
        caption.classList.remove('vjs-selected');
      });
      el.classList.add('vjs-selected');

      var tracks = this.player_.textTracks();
      for (var i = 0; i < tracks.length; i++) {
        var track = tracks[i];
        if (track.kind === 'captions') {
          this.player_.captionsLanguage = el.dataset.lang;
          track.mode = track.language === this.player_.captionsLanguage ? 'showing': 'disabled';
        }
      }
      this.player_.trigger('captionstrackchange');
      this.player_.trigger('subtitlestrackchange');
      this.player_.trigger('currentlanguagechanged');
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

      this.enabled_ = true;
      this.el_.setAttribute('aria-haspopup', 'true');
      this.el_.setAttribute('role', 'menuitem');

      this.on('click', this.onClick);
      this.on('mouseenter', function(event) {
        this.menu.el_.classList.add('is-visible');
      });
      this.on('mouseout', function(event) {
        this.menu.el_.classList.remove('is-visible');
      });

      this.createEl();
    },

    createItems: function createItems() {
      var items = arguments.length <= 0 || arguments[0] === undefined ? [] : arguments[0];
      var tracks = this.player_.textTracks();

      if (!tracks) {
        return items;
      }
      for (var i = 0; i < tracks.length; i++) {
        var track = tracks[i];
        // only add tracks that are of the appropriate kind and have a label
        if (track['kind'] === this.kind_) {
          items.push(new ToggleMenuItem(this.player_, {
            // MenuItem is selectable
            'track': track,
            'label': track.label,
            'enabledEvent': this.enabledEventName(),
            'disabledEvent': this.disabledEventName()
          }));
        }
      }
      return items;
    },

    styledSpan: function styledSpan() {
      return this.options_['style'];
    },
    enabledEventName: function enabledEventName() {
      return this.options_['enabledEvent'];
    },
    disabledEventName: function disabledEventName() {
      return this.options_['disabledEvent'];
    },
    buildCSSClass: function buildCSSClass() {
      return this.options_['cssClasses'];
    },
    createEl: function createEl(props, attributes) {
      props = props || {};
      props['className'] = this.buildCSSClass() + ' icon fa ' + this.styledSpan();
      props['tabIndex'] = 0;
      var el = MenuButton.prototype.createEl.call(this, arguments.tag, props, attributes);
      el.setAttribute('role', 'menuitem');
      el.setAttribute('aria-live', 'polite');
      el.classList += ' icon fa ' + this.styledSpan();
      el.classList.add('vjs-singleton');

      return el;
    },
    onClick: function onClick(event) {
      var el = event.currentTarget;
      el.classList.toggle('vjs-control-enabled');
      var eventName = this.hasClass('vjs-control-enabled') ? this.enabledEventName() : this.disabledEventName();
      this.player_.trigger(eventName);
    },

  });

  var toggleButton = function(options){
    if (this.tagAttributes.brightcove !== undefined) {
      this.controlBar.customControlSpacer.addChild('ToggleButton', options);
    } else {
      this.controlBar.addChild('ToggleButton', options);
    }
  };

  videojs.registerComponent('ToggleButton', ToggleButton);
  videojs.plugin('toggleButton', toggleButton);
});
