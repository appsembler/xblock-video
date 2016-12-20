
/** Javascript for VideoXBlock.student_view() */
function VideoXBlockStudentViewInit(runtime, element) {
  var stateHandlerUrl = runtime.handlerUrl(element, 'save_player_state');
  window.videoXBlockSaveStateHandlers = window.videoXBlockSaveStateHandlers || {};
  window.videoXBlockSaveStateHandlers[element.attributes['data-usage-id'].value] = stateHandlerUrl;

  var eventHandlerUrl = runtime.handlerUrl(element, 'publish_event');
  window.videoXBlockSaveEventHandlers = window.videoXBlockSaveEventHandlers || {};
  window.videoXBlockSaveEventHandlers[element.attributes['data-usage-id'].value] = eventHandlerUrl;

  window.videoXBlockListenerRegistered = window.videoXBlockListenerRegistered || false;

  /** Save video player state by POSTing it to VideoXBlock handler */
  function saveState(stateHandlerUrl, state) {
    $.ajax({
      type: "POST",
      url: stateHandlerUrl,
      data: JSON.stringify(state),
    })
    .done(function() {
      console.log('Player state saved successfully.');
    })
    .fail(function() {
      console.log('Failed to save player state.');
    });
  }

  /** Save video player analytic event by POSTing it to VideoXBlock handler */
  function publishEvent(eventHandlerUrl, data) {
    $.ajax({
      type: "POST",
      url: eventHandlerUrl,
      data: JSON.stringify(data),
    })
    .done(function() {
      console.log('Player event "' + data.eventType + '" published successfully.');
    })
    .fail(function() {
      console.log('Failed to publish player event.');
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
    if (event.data && event.data.action === 'save_state' &&
        window.videoXBlockSaveStateHandlers[event.data.xblockUsageId]) {
      saveState(window.videoXBlockSaveStateHandlers[event.data.xblockUsageId], event.data.state);
    }
    if (event.data && event.data.action === 'analytics' &&
        window.videoXBlockSaveEventHandlers[event.data.xblockUsageId]) {
      publishEvent(window.videoXBlockSaveEventHandlers[event.data.xblockUsageId], event.data.event_data)
    }
  }
}
