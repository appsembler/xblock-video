/**
 * Enable playback rates support for all VideoJS plugins.
 */

var Tech = videojs.getComponent('Tech');
Tech.prototype.featuresPlaybackRate = true;
