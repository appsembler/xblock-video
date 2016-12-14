domReady(function() {
  videojs('{{ video_player_id }}').ready(function(){

    // fire up the plugin
    var transcript = this.transcript({
      'showTrackSelector': false
    });

    // attach the widget to the page
    var transcriptContainer = document.querySelector('#transcript');
    transcriptContainer.appendChild(transcript.el());
  });
});
