
/** Javascript for VideoXBlock.student_view() */
function VideoXBlockStudentViewInit(runtime, element) {
  var handlerUrl = runtime.handlerUrl(element, 'save_player_state');
  window.videoXBlockSaveHandlers = window.videoXBlockSaveHandlers || {};
  window.videoXBlockSaveHandlers[element.attributes['data-usage-id'].value] = handlerUrl;
  window.videoXBlockListenerRegistered = window.videoXBlockListenerRegistered || false;

  /** Save video player satate by POSTing it to VideoXBlock handler */
  function saveState(handlerUrl, state) {
    $.ajax({
      type: "POST",
      url: handlerUrl,
      data: JSON.stringify(state),
    })
    .done(function() {
      console.log('Player state saved successfully.');
    })
    .fail(function() {
      console.log('Failed to save player state.');
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
    if (origin !== document.origin)
      // Discard a message received from another domain
      return;
    if (event.data && event.data.action === 'save_state' &&
        window.videoXBlockSaveHandlers[event.data.xblockUsageId]) {
      saveState(window.videoXBlockSaveHandlers[event.data.xblockUsageId], event.data.state);
    }
  }
}
