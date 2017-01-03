/**
 * This part is responsible for the player context menu.
 * Menu Options include:
 * - Play / Pause
 * - Mute / Unmute
 * - Fill browser / Unfill browser
 * - Speed
 *
 */

/**
 * Initialise player context menu with nested elements.
 */
domReady(function() {

  var videoPlayer = document.getElementById("{{ video_player_id }}");
  var dataSetup = JSON.parse(videoPlayer.getAttribute('data-setup'));
  var playbackRates = dataSetup.playbackRates;
  var docfrag = document.createDocumentFragment();
  // VideoJS Player() object necessary for context menu creation
  var player = videojs('{{ video_player_id }}');

  /**
   * Create elements of nested context submenu.
   */
  function createNestedContextSubMenu(e) {
    var target = e.target;

    // Generate nested submenu elements as document fragment
    var ulSubMenu = document.createElement('ul');
    ulSubMenu.className = 'vjs-contextmenu-ui-submenu';
    playbackRates.forEach(function(rate) {
      var liSubMenu = document.createElement('li');
      liSubMenu.className = 'vjs-submenu-item';
      liSubMenu.innerHTML = rate + 'x';
      ulSubMenu.appendChild(liSubMenu);
      liSubMenu.onclick = function() {
        player.playbackRate(parseFloat(rate));
      };
    });
    docfrag.appendChild(ulSubMenu);

    // Create nested submenu
    if (target.matches("li.vjs-menu-item")
        && target.innerText == getItem('speed').label
        && !target.querySelector('.vjs-contextmenu-ui-submenu') ) {
      target.appendChild(docfrag);
    }
  }

  // Delegate creation of a nested submenu for a context menu
  videoPlayer.addEventListener('mouseover', createNestedContextSubMenu);

  // Create context menu options
  var content = [{
    id: "play",
    label: 'Play',
    listener: function () {
      var item = getItem('play');
      if (player.paused()) {
        player.play();
        item['label'] = 'Pause';
      } else {
        player.pause();
        item['label'] = 'Play';
      }
    }}, {
    id: "mute",
    label: 'Mute',
    listener: function () {
      var item = getItem('mute');
      if (player.muted()){
        player.muted(false);
        item['label'] = 'Mute';
     } else {
        player.muted(true);
        item['label'] = 'Unmute';
      }
    }}, {
    id: "fullscreen",
    label: 'Fill browser',
    listener: function () {
      var item = getItem('fullscreen');
      if (player.isFullscreen()){
        player.exitFullscreen();
        item['label'] = 'Fill browser';
    } else {
        player.requestFullscreen();
        item['label'] = 'Unfill browser';
      }
    }}, {
    // Nested submenu creation is delegated to the player
    id: "speed",
    label: 'Speed'
    }
  ];

  // Fire up vjs-contextmenu-ui plugin
  player.contextmenuUI({content: content});

  // Update context menu labels
  var getItem = (function(contextmenuUI) {
    var hash = {};
    contextmenuUI.content.forEach(function(item) {
      hash[item.id] = item;
    });
    return function(id) {
      return hash[id];
    };
  }(player.contextmenuUI));

});
