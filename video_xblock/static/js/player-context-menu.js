/**
 * This part is responsible for the player context menu.
 * Menu Options include:
 * - Play / Pause
 * - Mute / Unmute
 * - Fill browser / Unfill browser
 * - Speed
 *
 */

domReady(function() {

  var videoPlayer = document.getElementById("{{ video_player_id }}");
  var dataSetup = JSON.parse(videoPlayer.getAttribute('data-setup'));
  var playbackRates = dataSetup.playbackRates;
  // VideoJS Player() object necessary for context menu creation
  var player = videojs('{{ video_player_id }}');

  // Delegate creation of a nested submenu for a context menu
  $(videoPlayer).on('mouseenter', 'li.vjs-menu-item:last', function(e) {
    e.preventDefault();

    // Create nested submenu
    if (e.target.classList.contains("vjs-menu-item") && !$(this).find('.vjs-contextmenu-ui-submenu').length) {
      var ulSubMenu = document.createElement('ul');
      ulSubMenu.className = 'vjs-contextmenu-ui-submenu';
      document.querySelectorAll('.vjs-contextmenu-ui-menu .vjs-menu-item')[3].appendChild(ulSubMenu);
      for (var i = 0; i < playbackRates.length; i++) {
        var liSubMenu = document.createElement('li');
        liSubMenu.className = 'vjs-submenu-item';
        liSubMenu.innerHTML = playbackRates[i] + 'x';
        ulSubMenu.appendChild(liSubMenu);
        liSubMenu.onclick = function(){
          player.playbackRate(parseFloat($(this).text()));
        }
      }
    }

    // Show nested submenu
    $('ul.vjs-contextmenu-ui-submenu').show();

    // Hide nested submenu
    $(this)
      .add('ul.vjs-contextmenu-ui-submenu')
      .add('div.vjs-contextmenu-ui-menu.vjs-menu-item')
      .on('mouseleave', function() {
        $('ul.vjs-contextmenu-ui-submenu').hide();
      });

  });

  // Fire up vjs-contextmenu-ui plugin, add context menu options
  player.contextmenuUI({
    content: [{
      label: 'Play',
      listener: function () {
        if (player.paused()) {
          player.play();
          player.contextmenuUI.content[0]['label'] = 'Pause';
        } else {
          player.pause();
          player.contextmenuUI.content[0]['label'] = 'Play';
        }
      }}, {
      label: 'Mute',
        listener: function () {
          if (player.muted()) {
            player.muted(false);
            player.contextmenuUI.content[1]['label'] = 'Mute';
          } else {
            player.muted(true);
            player.contextmenuUI.content[1]['label'] = 'Unmute';
          }
      }}, {
      label: 'Fill browser',
        listener: function () {
          if (player.isFullscreen()) {
            player.exitFullscreen();
            player.contextmenuUI.content[2]['label'] = 'Fill browser';
          } else {
            player.requestFullscreen();
            player.contextmenuUI.content[2]['label'] = 'Unfill browser';
          }
      }}, {
        // Nested submenu creation is delegated to the player
        label: 'Speed'}
    ]
  });

});
