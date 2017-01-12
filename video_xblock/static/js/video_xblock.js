
/** Javascript for VideoXBlock.student_view() */
function VideoXBlockStudentViewInit(runtime, element) {
  var stateHandlerUrl = runtime.handlerUrl(element, 'save_player_state');
  var eventHandlerUrl = runtime.handlerUrl(element, 'publish_event');
  var usageId = element.attributes['data-usage-id'].value;

  window.videoXBlockState = window.videoXBlockState || {};
  var handlers = window.videoXBlockState.handlers = window.videoXBlockState.handlers || {
    saveState: {},
    analytics: {}
  };
  handlers.saveState[usageId] = stateHandlerUrl;
  handlers.analytics[usageId] = eventHandlerUrl;

  /** Send data to server by POSTing it to appropriate VideoXBlock handler */
  function sendData(handlerUrl, data) {
    $.ajax({
      type: "POST",
      url: handlerUrl,
      data: JSON.stringify(data)
    })
    .done(function() {
      console.log('Data processed successfully.');
    })
    .fail(function() {
      console.log('Failed to process data');
    });
  }

  if (!window.videoXBlockListenerRegistered) {
    // Make sure we register event listener only once even if there are more than
    // one VideoXBlock on a page
    window.addEventListener("message", receiveMessage, false);
    window.videoXBlockListenerRegistered = true;
  }

  /**
   * Receive a message from child frames.
   * Expects a specific type of messages containing video player state to be saved on a server.
   * Pass the sate to `saveState()` for handling.
   */
  function receiveMessage(event) {
    var origin = event.origin || event.originalEvent.origin; // For Chrome, the origin property is in the event.originalEvent object.
    if (origin !== document.location.protocol + "//" + document.location.host)
      // Discard a message received from another domain
      return;
    try {
      if (event.data.action === "saveState") {
        updateTranscriptDownloadUrl(event.data.downloadTranscriptUrl);
      };

      var url = handlers[event.data.action][event.data.xblockUsageId];
      if (url) {
        sendData(url, event.data.info);
      }
    } catch (err){
      console.log(err)
    }
  };
  /** Updates transcript download url if it is enabled */
  function updateTranscriptDownloadUrl(downloadTranscriptUrl) {
    try {
      var downloadTranscriptUrl = downloadTranscriptUrl ? downloadTranscriptUrl : '#';
      document.getElementById('download-transcript-link').href = downloadTranscriptUrl;
    } catch (err){}
  }
}
