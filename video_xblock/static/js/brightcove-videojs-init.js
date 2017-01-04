domReady(function(){
  window.videojs = videojs;
  var player = videojs('{{ video_player_id }}');
  videojs.plugin('xblockEventPlugin', window.xblockEventPlugin);
  player.xblockEventPlugin();
  videojs.plugin('offset', window.vjsoffset);

  player.offset({
      "start": 0, // do not use quotes for this properties for correct plugin work
      "end": 0
  });

  videojs.plugin('videoJSSpeedHandler', window.videoJSSpeedHandler);
  player.videoJSSpeedHandler();
});
