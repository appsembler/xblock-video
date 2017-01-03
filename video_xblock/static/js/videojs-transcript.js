domReady(function() {
  videojs('{{ video_player_id }}').ready(function(){

    // fire up the plugin
    var transcript = this.transcript({
      'showTrackSelector': false
    });

    // attach the widget to the page
    var transcriptContainer = document.getElementById('transcript');
    transcriptContainer.appendChild(transcript.el());

    this.toggleButton({
      style: "fa-cc",
      enabledEvent: "captionenabled",
      disabledEvent: "captiondisabled",
      cssClasses: "vjs-custom-caption-button vjs-control",
    });
    this.toggleButton({
      style: "fa-quote-left",
      enabledEvent: "transcriptenabled",
      disabledEvent: "transcriptdisabled",
      cssClasses: "vjs-custom-transcript-button vjs-control",
    });
  });
});
