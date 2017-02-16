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
    var i;
    var field;
    for (i = 0; i < fields.length; i++) {
        field = fields[i];
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
    }
    return {values: values, defaults: notSet};
}
