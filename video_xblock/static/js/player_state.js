/**
 * This part is responsible for loading and saving player state.
 * State includes:
 * - Current time
 * - Playback rate
 * - Volume
 * - Muted
 *
 * State is loaded after VideoJs player is fully initialized.
 * State is saved at certain events.
 */

/** Run a callback when DOM is fully loaded */
var domReady = function(callback) {
  if (document.readyState === "interactive" || document.readyState === "complete") {
    callback();
  } else {
    document.addEventListener("DOMContentLoaded", callback);
  }
};

var player_state = {
  'volume': {{ player_state.volume }},
  'currentTime': {{ player_state.current_time }},
  'playbackRate': {{ player_state.playback_rate }},
  'muted': {{ player_state.muted | yesno:"true,false" }},
  'transcriptsEnabled': {{ player_state.transcripts_enabled | yesno:"true,false" }},
  'captionsEnabled': {{ player_state.captions_enabled | yesno:"true,false" }},
  'captionsLanguage': '{{ player_state.captions_language }}',
};

var xblockUsageId = window.location.hash.slice(1);

/** Restore default or previously saved player state */
var setInitialState = function (player, state) {
    var stateCurrentTime = state.currentTime;
    var playbackProgress = localStorage.getItem('playbackProgress');
    if (playbackProgress){
        playbackProgress=JSON.parse(playbackProgress);
        if (playbackProgress['{{ video_player_id }}'] && 
            playbackProgress['{{ video_player_id }}'] > stateCurrentTime) {
            stateCurrentTime = playbackProgress['{{ video_player_id }}'];
        }
    }
    if (stateCurrentTime > 0) {
        player.currentTime(stateCurrentTime);
    }
    player
        .volume(state.volume)
        .muted(state.muted)
        .playbackRate(state.playbackRate);
    player.transcriptsEnabled = state.transcriptsEnabled;
    player.captionsEnabled = state.captionsEnabled;
    player.captionsLanguage = state.captionsLanguage;
};

/**
 * Save player state by posting it in a message to parent frame.
 * Parent frame passes it to a server by calling VideoXBlock.save_state() handler.
 */
var saveState = function(){
  var player = this;
  var new_state = {
    'volume': player.volume(),
    'currentTime': player.ended()? 0 : Math.floor(player.currentTime()),
    'playbackRate': player.playbackRate(),
    'muted': player.muted(),
    'transcriptsEnabled': player.transcriptsEnabled,
    'captionsEnabled': player.captionsEnabled,
    'captionsLanguage': player.captionsLanguage,
  };

  if (JSON.stringify(new_state) !== JSON.stringify(player_state)) {
    console.log('Starting saving player state');
    player_state = new_state;
      parent.postMessage({'action': 'saveState', 'info': new_state, 'xblockUsageId': xblockUsageId},
          document.location.protocol + "//" + document.location.host);
  }
};

/**
 *  Save player progress in browser's local storage.
 *  We need it when user is switching between tabs.
 */
var saveProgressToLocalStore = function(){
  var player = this;
  var playbackProgress = localStorage.getItem('playbackProgress');
  if(playbackProgress == undefined){
      playbackProgress = '{}';
  }
  playbackProgress = JSON.parse(playbackProgress);
  playbackProgress['{{ video_player_id }}'] = player.ended() ? 0 : Math.floor(player.currentTime());
  localStorage.setItem('playbackProgress',JSON.stringify(playbackProgress));
};

domReady(function() {
  videojs('{{ video_player_id }}').ready(function() {
    var player = this;

    // Restore default or previously saved player state
    setInitialState(player, player_state);

    player
      .on('timeupdate', saveProgressToLocalStore)
      .on('volumechange', saveState)
      .on('ratechange', saveState)
      .on('play', saveState)
      .on('pause', saveState)
      .on('ended', saveState)
      .on('transcriptstatechanged', saveState)
      .on('captionstatechanged', saveState)
      .on('currentlanguagechanged', saveState);
  });

});
