/**
 * @file play-progress-bar.js
 */
import Component from '../../component.js';
import * as Fn from '../../utils/fn.js';
import formatTime from '../../utils/format-time.js';

/**
 * Shows play progress
 *
 * @param {Player|Object} player
 * @param {Object=} options
 * @extends Component
 * @class PlayProgressBar
 */
class PlayProgressBar extends Component {

  constructor(player, options) {
    super(player, options);
    this.updateDataAttr();
    this.on(player, 'timeupdate', this.updateDataAttr);
    player.ready(Fn.bind(this, this.updateDataAttr));

    if (options.playerOptions &&
        options.playerOptions.controlBar &&
        options.playerOptions.controlBar.progressControl &&
        options.playerOptions.controlBar.progressControl.keepTooltipsInside) {
      this.keepTooltipsInside = options.playerOptions.controlBar.progressControl.keepTooltipsInside;
    }

    if (this.keepTooltipsInside) {
      this.addClass('vjs-keep-tooltips-inside');
    }
  }

  /**
   * Create the component's DOM element
   *
   * @return {Element}
   * @method createEl
   */
  createEl() {
    return super.createEl('div', {
      className: 'vjs-play-progress vjs-slider-bar',
      innerHTML: `<span class="vjs-control-text"><span>${this.localize('Progress')}</span>: 0%</span>`
    });
  }

  updateDataAttr() {
    const time = (this.player_.scrubbing()) ? this.player_.getCache().currentTime : this.player_.currentTime();

    this.el_.setAttribute('data-current-time', formatTime(time, this.player_.duration()));
  }

}

Component.registerComponent('PlayProgressBar', PlayProgressBar);
export default PlayProgressBar;
