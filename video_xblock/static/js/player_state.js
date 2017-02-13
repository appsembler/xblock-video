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

var player_state_obj = JSON.parse('{{ player_state }}');
var player_state = {
    volume: player_state_obj.volume,
    currentTime: player_state_obj.current_time,
    playbackRate: player_state_obj.playback_rate,
    muted: player_state_obj.muted,
    transcriptsEnabled: player_state_obj.transcripts_enabled,
    captionsEnabled: player_state_obj.captions_enabled,
    captionsLanguage: player_state_obj.captions_language
};
var xblockUsageId = window.location.hash.slice(1);
var transcripts = {};
player_state_obj.transcripts.forEach(function loopTranscript(transcript) {
    transcripts[transcript.lang] = {
        'label': transcript.label,
        'url': transcript.url
    }
})
/** Get transcript url for current caption language */
var getDownloadTranscriptUrl = function(player) {
    var downloadTranscriptUrl;
    if (transcripts[player.captionsLanguage]) {
        downloadTranscriptUrl = transcripts[player.captionsLanguage].url;
    } else {
        downloadTranscriptUrl = '#';
    };
    return downloadTranscriptUrl;
}

/** Restore default or previously saved player state */
var setInitialState = function(player, state) {
    var stateCurrentTime = state.currentTime;
    var playbackProgress = localStorage.getItem('playbackProgress');
    if (playbackProgress){
        playbackProgress=JSON.parse(playbackProgress);
        if (playbackProgress['{{ video_player_id }}']) {
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
    // To switch off transcripts and captions state if doesn`t have transcripts with current captions language
    if (!transcripts[player.captionsLanguage]) {
        player.captionsEnabled = player.transcriptsEnabled = false;
    };
};

/**
 * Save player state by posting it in a message to parent frame.
 * Parent frame passes it to a server by calling VideoXBlock.save_state() handler.
 */
var saveState = function() {
    var player = this;
    var new_state = {
        volume: player.volume(),
        currentTime: player.ended()? 0 : player.currentTime(),
        playbackRate: player.playbackRate(),
        muted: player.muted(),
        transcriptsEnabled: player.transcriptsEnabled,
        captionsEnabled: player.captionsEnabled,
        captionsLanguage: player.captionsLanguage
    };
    if (JSON.stringify(new_state) !== JSON.stringify(player_state)) {
        console.log('Starting saving player state');
        player_state = new_state;
        parent.postMessage({
            action: 'saveState',
            info: new_state,
            xblockUsageId: xblockUsageId,
            downloadTranscriptUrl: getDownloadTranscriptUrl(player)
        },
        document.location.protocol + '//' + document.location.host
        );
    }
};

/**
 *  Save player progress in browser's local storage.
 *  We need it when user is switching between tabs.
 */
var saveProgressToLocalStore = function saveProgressToLocalStore() {
    var player = this;
    var playbackProgress = localStorage.getItem('playbackProgress');
    if (!playbackProgress) {
        playbackProgress = '{}';
    }
    playbackProgress = JSON.parse(playbackProgress);
    playbackProgress['{{ video_player_id }}'] = player.ended() ? 0 : player.currentTime();
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
        .on('languagechange', saveState);
    });
});
