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

  function createNestedContextSubMenu(e) {
    var target = e.target;

    if (target.matches("li.vjs-menu-item")
        && target.innerText == player.contextmenuUI.content[3].label
        && !target.querySelector('.vjs-contextmenu-ui-submenu') ) {

      // Create nested submenu
      var ulSubMenu = document.createElement('ul');
      ulSubMenu.className = 'vjs-contextmenu-ui-submenu';
      target.appendChild(ulSubMenu);
      for (var i = 0; i < playbackRates.length; i++) {
        var liSubMenu = document.createElement('li');
        liSubMenu.className = 'vjs-submenu-item';
        liSubMenu.innerHTML = playbackRates[i] + 'x';
        ulSubMenu.appendChild(liSubMenu);
        liSubMenu.onclick = function(){
          player.playbackRate(parseFloat(this.innerHTML));
        }
      }

      // Hide nested submenu
      var els = [target, ulSubMenu];
      els.forEach(function(item){
        item.onmouseout = function() { ulSubMenu.style.visibility = 'hidden' };
      });

      var liSpeedMenuItem = document.querySelectorAll('.vjs-contextmenu-ui-menu .vjs-menu-item')[3];
    }

    // Show nested submenu
    if (liSpeedMenuItem) {
      liSpeedMenuItem.addEventListener('mouseover', function(){
        document.querySelector('.vjs-contextmenu-ui-submenu').style.visibility = 'visible';
      })}
  }

  // Delegate creation of a nested submenu for a context menu
  videoPlayer.addEventListener('mouseover', createNestedContextSubMenu);

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
