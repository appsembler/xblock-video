/**
 * @file chapters-button.js
 */
import TextTrackButton from './text-track-button.js';
import Component from '../../component.js';
import TextTrackMenuItem from './text-track-menu-item.js';
import ChaptersTrackMenuItem from './chapters-track-menu-item.js';
import Menu from '../../menu/menu.js';
import * as Dom from '../../utils/dom.js';
import toTitleCase from '../../utils/to-title-case.js';

/**
 * The button component for toggling and selecting chapters
 * Chapters act much differently than other text tracks
 * Cues are navigation vs. other tracks of alternative languages
 *
 * @param {Object} player  Player object
 * @param {Object=} options Object of option names and values
 * @param {Function=} ready    Ready callback function
 * @extends TextTrackButton
 * @class ChaptersButton
 */
class ChaptersButton extends TextTrackButton {

  constructor(player, options, ready) {
    super(player, options, ready);
    this.el_.setAttribute('aria-label', 'Chapters Menu');
  }

  /**
   * Allow sub components to stack CSS class names
   *
   * @return {String} The constructed class name
   * @method buildCSSClass
   */
  buildCSSClass() {
    return `vjs-chapters-button ${super.buildCSSClass()}`;
  }

  /**
   * Create a menu item for each text track
   *
   * @return {Array} Array of menu items
   * @method createItems
   */
  createItems() {
    const items = [];
    const tracks = this.player_.textTracks();

    if (!tracks) {
      return items;
    }

    for (let i = 0; i < tracks.length; i++) {
      const track = tracks[i];

      if (track.kind === this.kind_) {
        items.push(new TextTrackMenuItem(this.player_, {track}));
      }
    }

    return items;
  }

  /**
   * Create menu from chapter buttons
   *
   * @return {Menu} Menu of chapter buttons
   * @method createMenu
   */
  createMenu() {
    const tracks = this.player_.textTracks() || [];
    let chaptersTrack;
    let items = this.items || [];

    for (let i = tracks.length - 1; i >= 0; i--) {

      // We will always choose the last track as our chaptersTrack
      const track = tracks[i];

      if (track.kind === this.kind_) {
        chaptersTrack = track;

        break;
      }
    }

    let menu = this.menu;

    if (menu === undefined) {
      menu = new Menu(this.player_);

      const title = Dom.createEl('li', {
        className: 'vjs-menu-title',
        innerHTML: toTitleCase(this.kind_),
        tabIndex: -1
      });

      menu.children_.unshift(title);
      Dom.insertElFirst(title, menu.contentEl());
    } else {
      // We will empty out the menu children each time because we want a
      // fresh new menu child list each time
      items.forEach(item => menu.removeChild(item));
      // Empty out the ChaptersButton menu items because we no longer need them
      items = [];
    }

    if (chaptersTrack && (chaptersTrack.cues === null || chaptersTrack.cues === undefined)) {
      chaptersTrack.mode = 'hidden';

      const remoteTextTrackEl = this.player_.remoteTextTrackEls().getTrackElementByTrack_(chaptersTrack);

      if (remoteTextTrackEl) {
        remoteTextTrackEl.addEventListener('load', (event) => this.update());
      }
    }

    if (chaptersTrack && chaptersTrack.cues && chaptersTrack.cues.length > 0) {
      const cues = chaptersTrack.cues;

      for (let i = 0, l = cues.length; i < l; i++) {
        const cue = cues[i];

        const mi = new ChaptersTrackMenuItem(this.player_, {
          cue,
          track: chaptersTrack
        });

        items.push(mi);

        menu.addChild(mi);
      }
    }

    if (items.length > 0) {
      this.show();
    }
    // Assigning the value of items back to this.items for next iteration
    this.items = items;
    return menu;
  }
}

ChaptersButton.prototype.kind_ = 'chapters';
ChaptersButton.prototype.controlText_ = 'Chapters';

Component.registerComponent('ChaptersButton', ChaptersButton);
export default ChaptersButton;
