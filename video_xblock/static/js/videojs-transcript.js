domReady(function() {
  videojs('{{ video_player_id }}').ready(function(){

    // fire up the plugin
    var transcript = this.transcript({
      'showTrackSelector': false,
      'showTitle': false
    });

    // attach the widget to the page
    var transcriptContainer = document.getElementById('transcript');

    // Show or hide the transcripts block depending on the transcript state
    if (!this.transcriptsEnabled){
      transcriptContainer.className += " is-hidden";
    };
    transcriptContainer.appendChild(transcript.el());

    this.on('transcriptenabled', function(){
      transcriptContainer.classList.toggle('is-hidden');
      this.transcriptsEnabled = true;
      this.trigger('transcriptstatechanged');
    });
    this.on('transcriptdisabled', function(){
      transcriptContainer.classList.toggle('is-hidden');
      this.transcriptsEnabled = false;
      this.trigger('transcriptstatechanged');
    });

    this.toggleButton({
      style: "fa-cc",
      enabledEvent: "captionenabled",
      disabledEvent: "captiondisabled",
      cssClasses: "vjs-custom-caption-button vjs-control",
    });
    var cssClasses = "vjs-custom-transcript-button vjs-control";
    if (this.transcriptsEnabled){
      cssClasses += ' vjs-control-enabled';
    };
    this.toggleButton({
      style: "fa-quote-left",
      enabledEvent: "transcriptenabled",
      disabledEvent: "transcriptdisabled",
      cssClasses: cssClasses,
    });
  });
});
