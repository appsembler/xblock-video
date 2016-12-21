domReady(function() {
  videojs('{{ video_player_id }}').ready(function() {

    // order tabIndex in player control
    var orderTabIndex = function orderTabIndex(_player) {
        var controlBarActions = Object.keys(_player.controlBar.childNameIndex_);
        var controlsTabOrder = [
            'progressControl',
            'playToggle',
            'playbackRateMenuButton',
            'volumeMenuButton',
            'resolutionSwitcher',
            'fullscreenToggle',
            'captionsButton'
          ];
        var controlsMap = {
            'progressControl': _player.controlBar.childNameIndex_.progressControl.seekBar.el_,
            'playToggle': _player.controlBar.childNameIndex_.playToggle.el_,
            'captionsButton': _player.controlBar.childNameIndex_.captionsButton.el_,
            'volumeMenuButton': _player.controlBar.childNameIndex_.volumeMenuButton.volumeBar.el_,
            'fullscreenToggle': _player.controlBar.childNameIndex_.fullscreenToggle.el_,
            'resolutionSwitcher': _player.controlBar.resolutionSwitcher,
            'playbackRateMenuButton': _player.controlBar.childNameIndex_.playbackRateMenuButton.el_
          };

        // Plugin resolution switcher doesn't add it's control to controlBar
        controlBarActions.push('resolutionSwitcher');
        // Swith off tabIndex for volumeMenuButton and free slot for volumeBar
        _player.controlBar.childNameIndex_.volumeMenuButton.el_.tabIndex = -1;

        controlBarActions.forEach(function(action) {
          var el = controlsMap[action] || _player.controlBar.childNameIndex_[action].el_;
          var index = controlsTabOrder.indexOf(action);
          el.tabIndex = index === -1 ? -1 : index + 1;
        });
    };

    orderTabIndex(this);

  });

});
