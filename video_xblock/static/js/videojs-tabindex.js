/**
 * This part is responsible for the order tabindex.
 * 
 * Determine and call the function orderTabIndex.
 * 
 * orderTabIndex - is function what rearrange controlBar elements
 * in right order
 */

domReady(function() {
  videojs('{{ video_player_id }}').ready(function() {

    /** Order tabIndex in player control */
    var orderTabIndex = function orderTabIndex(_player) {
        var controlBar;
        if (_player.tagAttributes.brightcove === undefined){
            controlBar = _player.controlBar.childNameIndex_;
        } else {
            controlBar = _player.controlBar;
        };
        var controlBarActions = Object.keys(controlBar);
        var controlsTabOrder = [
            'progressControl',
            'playToggle',
            'playbackRateMenuButton',
            'volumeMenuButton',
            'fullscreenToggle',
            'captionsButton'
          ];
        var controlsMap = {
            'progressControl': controlBar.progressControl.seekBar.el_,
            'playToggle': controlBar.playToggle.el_,
            'captionsButton': controlBar.captionsButton.el_,
            'volumeMenuButton': controlBar.volumeMenuButton.volumeBar.el_,
            'fullscreenToggle': controlBar.fullscreenToggle.el_,
            'playbackRateMenuButton': controlBar.playbackRateMenuButton.el_
          };

        // Switch off tabIndex for volumeMenuButton and free slot for volumeBar
        controlBar.volumeMenuButton.el_.tabIndex = -1;

        controlBarActions.forEach(function(action) {
          var el = controlsMap[action] || controlBar[action].el_;
          if (el) {
            var index = controlsTabOrder.indexOf(action);
            el.tabIndex = index === -1 ? -1 : index + 1;
          }
        });
    };

    orderTabIndex(this);

  });

});
