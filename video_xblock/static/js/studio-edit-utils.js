/**
 * Auxiliary functions for studio editor modal's JS.
 */

/**
 * Prepare data to be saved to video xblock.
 */
function fillValues(fields) {
    'use strict';
    var values = {};
    var notSet = []; // List of field names that should be set to default values
    fields.forEach(function(field) {
        if (field.isSet()) {
            values[field.name] = field.val();
        } else {
            notSet.push(field.name);
        }
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        if (field.hasEditor()) {
            field.removeEditor();
        }
    });
    return {values: values, defaults: notSet};
}


/**
 * Display message with results of a performed action (e.g. a transcript manual or automatic upload).
 * @param {String}         message Status message for user to be displayed.
 * @param {String}         type    Message type: 'success' or 'error'.
 * @param {jQuery Element} $el     Container element where message should be displayed.
 */
function showStatus(message, type, $el) {
    'use strict';
    var fiveSeconds = 5000;
    // Only one success message is to be displayed at once
    $('.api-response').empty();

    $el.removeClass('status-error status-success is-hidden').addClass('status-' + type)
       .text(message);

    setTimeout(function() {
        $el.addClass('is-hidden');
    }, fiveSeconds);
}
