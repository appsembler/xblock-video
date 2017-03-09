/**
 * Default transcripts functionality is represented here.
 */

/**
 * Create elements to display messages with status on actions with default transcripts.
 */
function createStatusMessageElement(langCode, actionSelector) {
    'use strict';

    var parentSelector = '';
    var messageSelector = '.api-response.' + actionSelector + '.' + langCode + '.status';
    var $messageUpload;
    if (actionSelector === 'upload-default-transcript') {
        parentSelector = 'available-default-transcripts-section';
    } else if (actionSelector === 'remove-default-transcript') {
        parentSelector = 'enabled-default-transcripts-section';
    }

    if ($(messageSelector).length === 0) {
        $messageUpload = $('<div>',
            {class: messageSelector});
        $messageUpload.appendTo($('.' + parentSelector + ':visible').last());
    }
}

/**
 *  Manage default transcripts labels display depending on enabled/available subs presence.
 */
function setDisplayDefaultTranscriptsLabel(isNotDisplayedDefaultSub, labelElement) {
    'use strict';
    if (isNotDisplayedDefaultSub) {
        labelElement.addClass('is-hidden');
    } else {
        labelElement.removeClass('is-hidden');
    }
}

/**
 *  Store all the default transcripts, fetched at document load, and their languages' codes.
 */
function getInitialDefaultTranscriptsData() {
    'use strict';
    var $defaultSubs = $('.initial-default-transcript');
    var initialDefaultTranscripts = [];
    var langCodes = [];
    var langCode;
    var langLabel;
    var downloadUrl;
    var newSub;
    $defaultSubs.each(function() {
        langCode = $(this).attr('data-lang-code');
        langLabel = $(this).attr('data-lang-label');
        downloadUrl = $(this).attr('data-download-url');
        newSub = {lang: langCode, label: langLabel, url: downloadUrl};
        initialDefaultTranscripts.push(newSub);
        langCodes.push(langCode);
    });
    return [initialDefaultTranscripts, langCodes];
}

/** Wrapper for getting of a default transcripts array. */
function getDefaultTranscriptsArray(defaultTranscriptType) {
    'use strict';
    var defaultTranscriptsArray = [];
    var code;
    $('.' + defaultTranscriptType + '-default-transcripts-section .default-transcripts-label:visible').each(function() {
        code = $(this).attr('value');
        defaultTranscriptsArray.push(code);
    });
    return defaultTranscriptsArray;
}

/** Create available transcript. */
function createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData) {
    'use strict';
    var langCode = defaultTranscript.lang;
    var langLabel = defaultTranscript.label;
    var initialDefaultTranscripts = initialDefaultTranscriptsData[0];
    var initialDefaultTranscriptsLangCodes = initialDefaultTranscriptsData[1];
    // Get all the currently available transcripts
    var allAvailableTranscripts = getDefaultTranscriptsArray('available');
    // Create a new available transcript if stored on a platform and doesn't already exist on video xblock
    var isNotDisplayedAvailableTranscript = $.inArray(langCode, allAvailableTranscripts) === -1;
    var isStoredVideoPlatform = $.inArray(langCode, initialDefaultTranscriptsLangCodes) !== -1;
    var $availableLabel;
    var isHiddenAvailableLabel;
    var $newAvailableTranscriptBlock;
    var downloadUrlApi;
    if (isNotDisplayedAvailableTranscript && isStoredVideoPlatform) {
        // Show label of available transcripts if no such label is displayed
        $availableLabel = $('div.custom-field-section-label.available-transcripts');
        isHiddenAvailableLabel = !$('div.custom-field-section-label.available-transcripts:visible').length;
        if (isHiddenAvailableLabel) { $availableLabel.removeClass('is-hidden'); }
        // Create a default (available) transcript block
        $newAvailableTranscriptBlock = $('.available-default-transcripts-section:hidden').clone();
        $newAvailableTranscriptBlock.removeClass('is-hidden').appendTo($('.default-transcripts-wrapper'));
        $('.default-transcripts-label:visible').last()
            .attr('value', langCode)
            .text(langLabel);
        // Get url for a transcript fetching from the API
        downloadUrlApi = getTranscriptUrl(initialDefaultTranscripts, langCode); // External url for API call
        // Update attributes
        $('.default-transcripts-action-link.upload-default-transcript').last()
            .attr({'data-lang-code': langCode, 'data-lang-label': langLabel, 'data-download-url': downloadUrlApi});
        // Create elements to display status messages on available transcript upload
        createStatusMessageElement(langCode, 'upload-default-transcript');
    }
}

/**
 * Display a transcript in a list of enabled transcripts. Listeners on removal are bound in studio editor js.
 *
 * Arguments:
 * defaultTranscript (Array): Array containing transcript data (languages, urls).
 * downloadUrlServer (String): External url to download a resource from a server.
 *
 */
function createEnabledTranscriptBlock(defaultTranscript, downloadUrlServer) {
    'use strict';
    var langCode = defaultTranscript.lang;
    var langLabel = defaultTranscript.label;
    var $availableTranscriptBlock = $('div[value=' + langCode + ']')
        .closest('div.available-default-transcripts-section:visible');
    var $enabledLabel = $('div.custom-field-section-label.enabled-transcripts');
    var $availableLabel = $('div.custom-field-section-label.available-transcripts');
    var allEnabledTranscripts;
    var isNotDisplayedEnabledTranscript;
    var isHiddenEnabledLabel;
    var $newEnabledTranscriptBlock;
    var $lastEnabledTranscriptBlock;
    var $hiddenEnabledTranscriptBlock;
    var $parentElement;
    var $insertedEnabledTranscriptBlock;
    var $insertedEnabledTranscriptLabel;
    var $downloadElement;
    var $removeElement;
    var areNotVisibleAvailableTranscripts;

    // Remove a transcript of choice from the list of available ones
    $availableTranscriptBlock.remove();
    // Hide label of available transcripts if no such items left and if default transcripts are shown
    areNotVisibleAvailableTranscripts = !$('div.available-default-transcripts-section:visible').length;
    if (areNotVisibleAvailableTranscripts) {
        $availableLabel.addClass('is-hidden');
    }
    // Get all the currently enabled transcripts
    allEnabledTranscripts = getDefaultTranscriptsArray('enabled');
    // Create a new enabled transcript if it doesn't already exist in a video xblock
    isNotDisplayedEnabledTranscript = $.inArray(langCode, allEnabledTranscripts) === -1;
    if (isNotDisplayedEnabledTranscript) {
        // Display label of enabled transcripts if hidden
        isHiddenEnabledLabel = $('div.custom-field-section-label.enabled-transcripts').hasClass('is-hidden');
        if (isHiddenEnabledLabel) { $enabledLabel.removeClass('is-hidden'); }
        // Create a default (enabled) transcript block
        $newEnabledTranscriptBlock = $('.enabled-default-transcripts-section:hidden').clone();
        // Insert a new default transcript block
        $lastEnabledTranscriptBlock = $('.enabled-default-transcripts-section:visible').last();
        $parentElement = (isHiddenEnabledLabel) ? $enabledLabel : $lastEnabledTranscriptBlock;
        if ($parentElement) {
            $newEnabledTranscriptBlock.removeClass('is-hidden').insertAfter($parentElement);
        } else {
            $hiddenEnabledTranscriptBlock = $('.enabled-default-transcripts-section:hidden');
            $newEnabledTranscriptBlock.removeClass('is-hidden').insertBefore($hiddenEnabledTranscriptBlock);
        }
        // Update attributes
        $insertedEnabledTranscriptBlock =
            $('.enabled-default-transcripts-section:not(.is-hidden)').last();
        $insertedEnabledTranscriptLabel =
            $insertedEnabledTranscriptBlock.find('.default-transcripts-label');
        $insertedEnabledTranscriptLabel.attr('value', langCode).text(langLabel);
        $downloadElement = $insertedEnabledTranscriptBlock
            .find('.default-transcripts-action-link.download-transcript.download-setting');
        $downloadElement.attr(
            {'data-lang-code': langCode, 'data-lang-label': langLabel, href: downloadUrlServer}
        );
        $removeElement = $insertedEnabledTranscriptBlock
            .find('.default-transcripts-action-link.remove-default-transcript');
        $removeElement.attr({'data-lang-code': langCode, 'data-lang-label': langLabel});
    }
}

/** Remove enabled transcript of choice. */
function removeEnabledTranscriptBlock(enabledTranscript, initialDefaultTranscriptsData) {
    'use strict';
    var langCode = enabledTranscript.lang;
    var langLabel = enabledTranscript.label;
    var initialDefaultTranscriptsLangCodes = initialDefaultTranscriptsData[1];
    // Remove enabled transcript of choice
    var $enabledTranscriptBlock = $('div[value=' + langCode + ']').closest('div.enabled-default-transcripts-section');
    var $enabledLabel = $('div.custom-field-section-label.enabled-transcripts');
    var allEnabledTranscripts;
    var isSuccessfulRemoval;
    var isStoredVideoPlatform;
    var isNotPresentEnabledTranscripts;
    var message, status;
    var SUCCESS = 'success';
    var ERROR = 'error';
    $enabledTranscriptBlock.remove();
    isNotPresentEnabledTranscripts = !$('div.enabled-default-transcripts-section:visible').length;
    // Hide label of enabled transcripts if no such items left
    if (isNotPresentEnabledTranscripts) {
        $enabledLabel.addClass('is-hidden');
    }
    // Create elements to display status messages on enabled transcript removal
    createStatusMessageElement(langCode, 'remove-default-transcript');
    // Get all the currently enabled transcripts
    allEnabledTranscripts = getDefaultTranscriptsArray('enabled');
    isSuccessfulRemoval = $.inArray(langCode, allEnabledTranscripts) === -1; // Is not in array
    isStoredVideoPlatform = $.inArray(langCode, initialDefaultTranscriptsLangCodes) !== -1;  // Is in array
    // Display message with results of removal
    if (isSuccessfulRemoval && isStoredVideoPlatform) {
        message = gettext('{langLabel} transcripts are successfully removed from the list of enabled ones.');
        status = SUCCESS;
    } else if (isSuccessfulRemoval && !isStoredVideoPlatform) {
        message = gettext('{langLabel} transcripts are removed, but can not be uploaded from the video platform.');
        status = ERROR;
    } else {
        message = gettext('{langLabel} transcripts are not neither removed nor added to the list of available ones.');
        status = ERROR;
    }
    showStatus(
        message.replace('{langLabel}', langLabel),
        status,
        $('.api-response.remove-default-transcript.' + langCode + '.status')
    );
}

/**
 * Remove all enabled transcripts.
 */
function removeAllEnabledTranscripts(initialDefaultTranscriptsData, bindFunction) {
    'use strict';
    var $currentEnabledTranscripts = $('.default-transcripts-action-link.remove-default-transcript:visible');
    $currentEnabledTranscripts.each(function(index, elem) {
        var code = elem.dataset.langCode;
        var label = elem.dataset.langLabel;
        var url = '';
        var defaultTranscript = {lang: code, label: label, url: url};
        removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        bindFunction(code, label);
    });
}
