/**
 * Auxiliary functions for studio editor modal's JS.
 */

var gettext = gettext || function(str) { return str; } // eslint-disable-line

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
    });
    return {values: values, defaults: notSet};
}


/**
 * Display message with results of a performed action (e.g. a transcript manual or automatic upload).
 * @param {jQuery Elements} $el     Container elements where message should be displayed.
 * @param {String}          type    Message type: 'success' or 'error'.
 * @param {String}          message Status message for user to be displayed.
 */
function showStatus($el, type, message) {
    'use strict';
    // TODO: Convert into class and ensure previously set timeouts are cleared
    //       before setting new timeout

    var msgShowTime = 5000; // 5 seconds

    $el.removeClass('status-error status-success is-hidden').addClass('status-' + type)
       .text(message);

    setTimeout(function() {
        $el.addClass('is-hidden');
    }, msgShowTime);
}
