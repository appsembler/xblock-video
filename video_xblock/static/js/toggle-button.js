/**
 * The initial caption and transcript button.
 * Add "ToggleButton" to videojs as plugin.
 */

domReady(function() {
  var Button = videojs.getComponent('Button');
  var ToggleButton = videojs.extend(Button, {
    // base class for create buttons for caption and transcripts
    constructor: function constructor(player, options) {
      Button.call(this, player, options);
      this.on('click', this.onClick);
      this.createEl();
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
      props['className'] = this.buildCSSClass();
      props['innerHTML'] = '<div class="vjs-control-content icon fa ' + this.styledSpan() + '"></div>';
      props['tabIndex'] = 0;
      var el = Button.prototype.createEl.call(this, arguments.tag, props, attributes);
      el.setAttribute('role', 'button');
      el.setAttribute('aria-live', 'polite');
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
