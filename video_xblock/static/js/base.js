/** Run a callback when DOM is fully loaded */
var domReady = function(callback) {
    'use strict';
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
};
