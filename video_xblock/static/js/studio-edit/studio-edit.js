/* global createAvailableTranscriptBlock disableOption removeStandardTranscriptBlock getInitialDefaultTranscriptsData
removeEnabledTranscriptBlock bindUploadListenerAvailableTranscript pushTranscript pushTranscriptsValue
createEnabledTranscriptBlock createTranscriptBlock parseRelativeTime removeAllEnabledTranscripts tinyMCE baseUrl
validateTranscripts fillValues validateTranscriptFile removeTranscriptBlock clickUploader
languageChecker getHandlers */
/**
    Set up the Video xblock studio editor. This part is responsible for validation and sending of the data to a backend.
    Reference:
        https://github.com/edx/xblock-utils/blob/v1.0.3/xblockutils/templates/studio_edit.html
*/
function StudioEditableXBlock(runtime, element) {
    'use strict';

    var fields = [];
    var tryRefreshPageMessage = gettext(
        'This may be happening because of an error with our server or your internet connection. ' +
        'Try refreshing the page or making sure you are online.'
    );
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin
    var $defaultTranscriptsSwitcher = $('input.default-transcripts-switch-input');
    var $enabledLabel = $('div.custom-field-section-label.enabled-transcripts');
    var $availableLabel = $('div.custom-field-section-label.available-transcripts');
    var $modalHeaderTabs = $('.editor-modes.action-list.action-modes');
    var currentTabName;
    var isNotDummy = $('#xb-field-edit-href').val() !== '';
    var SUCCESS = 'success';
    var ERROR = 'error';

    var transcriptsValue = [];
    var disabledLanguages = [];
    var $fileUploader = $('.input-file-uploader', element);
    var $defaultTranscriptUploader = $('.upload-default-transcript');
    var $defaultTranscriptRemover = $('.remove-default-transcript');
    var $standardTranscriptUploader = $('.add-transcript');
    var $standardTranscriptRemover = $('.remove-action');
    var $langChoiceItem = $('.language-transcript-selector', element);
    var $videoApiAuthenticator = $('#video-api-authenticate', element);
    var gotTranscriptsValue = $('input[data-field-name="transcripts"]').val();
    var runtimeHandlers = getHandlers(runtime, element);
    var currentLanguageCode;
    var initialDefaultTranscriptsData = getInitialDefaultTranscriptsData();
    var initialDefaultTranscripts = initialDefaultTranscriptsData[0];

    /** Toggle studio editor's current tab.
     */
    function toggleEditorTab(event, tabName) {
        var $tabDisable;
        var $tabEnable;
        var $otherTabName;
        if (tabName === 'Basic') {
            $tabEnable = $('.list-input.settings-list.basic');
            $tabDisable = $('.list-input.settings-list.advanced');
            $otherTabName = 'Advanced';
        } else if (tabName === 'Advanced') {
            $tabEnable = $('.list-input.settings-list.advanced');
            $tabDisable = $('.list-input.settings-list.basic');
            $otherTabName = 'Basic';
        }
        $(event.currentTarget).addClass('current');
        $('.edit-menu-tab[data-tab-name=' + $otherTabName + ']').removeClass('current');
        $tabDisable.addClass('is-hidden');
        $tabEnable.removeClass('is-hidden');
    }

    // Create advanced and basic tabs
    (function() {
        if (isNotDummy) {
            $modalHeaderTabs
                .append(
                    '<li class="inner_tab_wrap">' +
                    '<button class="edit-menu-tab" data-tab-name="Advanced">Advanced</button>' +
                    '</li>',
                    '<li class="inner_tab_wrap">' +
                    '<button class="edit-menu-tab current" data-tab-name="Basic">Basic</button>' +
                    '</li>');
            // Bind listeners to the toggle buttons
            $('.edit-menu-tab').click(function(event) {
                currentTabName = $(event.currentTarget).attr('data-tab-name');
                toggleEditorTab(event, currentTabName);
            });
        }
    }());

    /** Wrapper function for dispatched ajax calls.
     */
    function ajaxCallDispatch(method, suffix, handlerMethod) {
        return $.ajax({
            type: method,
            url: runtime.handlerUrl(element, handlerMethod, suffix),
            data: '{}'
        });
    }

    /** This function is used for Brightcove HLS debugging
     *  profile: ingest profile to use for re-transcode job.
     *  Accepted values: default, autoquality, encryption.
     */
    function uiDispatch(method, suffix) {
        return ajaxCallDispatch(method, suffix, 'ui_dispatch');
    }

    /** Dispatch a specific method.
     */
    function dispatch(method, suffix) {
        return ajaxCallDispatch(method, suffix, 'dispatch');
    }

    /** Submit Brightcove re-ntranscode for video content protection.
     */
    function submitBCReTranscode(profile) {
        $.when(
            dispatch('POST', 'submit_retranscode_' + profile)
        ).then(function(response) {
            $('#brightcove-retranscode-status').html(
                'Your retranscode request was successfully submitted to Brightcove VideoCloud. ' +
                'It takes few minutes to process it. Job id ' + response.id);
        });
    }

    /** Load Brightcove video information.
     */
    function bcLoadVideoTechInfo() {
        $.when(
            dispatch('POST', 'get_video_tech_info')
        ).then(function(response) {
            $('#bc-tech-info-renditions').html(response.renditions_count);
            $('#bc-tech-info-autoquality').html(response.auto_quality);
            $('#bc-tech-info-encryption').html(response.encryption);
        });
    }

    /** Fetch re-transcode status.
     */
    function getReTranscodeStatus() {
        $.when(
            dispatch('POST', 'retranscode-status')
        ).then(function(data) {
            $('#brightcove-retranscode-status').html(data);
        });
    }

    /** Customize settings display.
     */
    function showBackendSettings() {
        $.when(
            uiDispatch('GET', 'can-show-backend-settings')
        ).then(function(response) {
            if (response.data.canShow) {
                $('#brightcove-advanced-settings').toggleClass('is-hidden', false);
                bcLoadVideoTechInfo();
                getReTranscodeStatus();
            }
        });
    }

    $('#submit-re-transcode').click(function() {
        var profile = $('#xb-field-edit-retranscode-options').val();
        submitBCReTranscode(profile);
    }
    );

    $('#settings-tab').ready(function() {
        showBackendSettings();
    });
    /**
     * Is there a more specific error message we can show?
     * @param  {String} responseText JSON received from ajax call
     * @return {String}              Error message extracted from input JSON or a portion of input text
     */
    function extractErrorMessage(responseText) {
        var message;
        try {
            message = JSON.parse(responseText).error;
            if (typeof message === 'object' && message.messages) {
                // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                message = $.map(message.messages, function(msg) { return msg.text; }).join(', ');
            }
            return message;
        } catch (error) { // SyntaxError thrown by JSON.parse
            return responseText.substr(0, 300);
        }
    }
    /**
     * Bind removal listener to a newly created enabled transcript.
     */
    function bindRemovalListenerEnabledTranscript(langCode, langLabel, downloadUrlServer) {
        var $removeElement = $(
            '.default-transcripts-action-link.remove-default-transcript[data-lang-code=' + langCode + ']');
        $removeElement.click(function(event) {
            var defaultTranscript = {
                lang: langCode,
                label: langLabel,
                url: downloadUrlServer
            };
            // Affect default transcripts
            removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            bindUploadListenerAvailableTranscript(langCode, langLabel); // eslint-disable-line no-use-before-define
            // Affect standard transcripts
            removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages);
            disableOption($langChoiceItem, disabledLanguages);
            event.preventDefault();
        });
    }
    /**
     * Upload a transcript available on a video platform to video xblock and update displayed default transcripts.
     */
    function uploadDefaultTranscriptsToServer(data) {
        var message, status;

        $.ajax({
            type: 'POST',
            url: runtimeHandlers.uploadDefaultTranscript,
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(response) {
            var newLang = response.lang;
            var newLabel = response.label;
            var newUrl = response.url;
            var source = response.source;
            // Add a default transcript to the list of enabled ones
            var downloadUrl = runtimeHandlers.downloadTranscript + '?' + newUrl;
            var defaultTranscript = {
                lang: newLang,
                label: newLabel,
                url: downloadUrl,
                source: source
            };
            // Create a standard transcript
            pushTranscript(newLang, newLabel, newUrl, source, '', transcriptsValue);
            pushTranscriptsValue(transcriptsValue);
            createEnabledTranscriptBlock(defaultTranscript, downloadUrl);
            bindRemovalListenerEnabledTranscript(newLang, newLabel, newUrl);
            message = response.success_message;
            status = SUCCESS;
        })
        .fail(function(jqXHR) {
            message = tryRefreshPageMessage;
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message += extractErrorMessage(jqXHR.responseText);
            }
            status = ERROR;
        })
        .always(function() {
            showStatus(
                $('.api-response.upload-default-transcript.' + currentLanguageCode + '.status'),
                status,
                message
            );
        });
    }
    /**
     * Bind upload listener to a newly created available transcript.
     */
    function bindUploadListenerAvailableTranscript(langCode, langLabel) {
        var $uploadElement = $(
            '.default-transcripts-action-link.upload-default-transcript[data-lang-code=' + langCode + ']');
        $uploadElement.click(function() {
            // Get url for a transcript fetching from the API
            var downloadUrlApi = getTranscriptUrl(initialDefaultTranscripts, langCode);
            var defaultTranscript = {
                lang: langCode,
                label: langLabel,
                url: downloadUrlApi,
                source: $fileUploader.data('source-default')
            };
            uploadDefaultTranscriptsToServer(defaultTranscript);
            // Affect standard transcripts
            createTranscriptBlock(langCode, langLabel, transcriptsValue, runtimeHandlers.downloadTranscript);
        });
    }
    /** Field Changed event */
    function fieldChanged($wrapper, $resetButton) {
        // Field value has been modified:
        $wrapper.addClass('is-set');
        $resetButton.removeClass('inactive').addClass('active');
    }

    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        var contextId = $wrapper.context.id;
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type === 'boolean') {  // eslint-disable-line
                    return (val === 'true' || val === '1');  // eslint-disable-line
                } else if (type === 'integer') {  // eslint-disable-line
                    return parseInt(val, 10);
                } else if (type === 'float') {  // eslint-disable-line
                    return parseFloat(val);
                } else if (['generic', 'list', 'set'].indexOf(type) !== -1) {
                    val = val.trim();
                    if (val === '') {
                        val = null;
                    } else {
                        val = JSON.parse(val); // TODO: handle parse errors
                    }
                    return val;
                } else if (type === 'string' && (
                    contextId === 'xb-field-edit-start_time'
                    || contextId === 'xb-field-edit-end_time')) {
                    return parseRelativeTime(val);
                } else {
                    return val;
                }
            }
        });
        $field.bind('change input paste', fieldChanged($wrapper, $resetButton));
        $resetButton.click(function() {
            // Use attr instead of data to force treating the default value as a string
            $field.val($wrapper.attr('data-default'));
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
            // Remove all enabled default transcripts
            removeAllEnabledTranscripts(initialDefaultTranscriptsData, bindUploadListenerAvailableTranscript);
        });

        if (type === 'datepicker' && datepickerAvailable) {
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: 'm/d/yy'});
        }
    });

    $(element).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $optionList.find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($optionList.val()));
                    }
                });
                return val;
            }
        });
        $checkboxes.bind('change input', fieldChanged($wrapper, $resetButton));

        $resetButton.click(function() {
            var defaults = JSON.parse($wrapper.attr('data-default'));
            $checkboxes.each(function() {
                var val = JSON.parse($(this).val());
                $(this).prop('checked', defaults.indexOf(val) > -1);
            });
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
            // Remove all enabled default transcripts
            removeAllEnabledTranscripts(initialDefaultTranscriptsData, bindUploadListenerAvailableTranscript);
        });
    });

    /** Submit studio editor settings.
     */
    function studioSubmit(data) {
        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        var message;
        runtime.notify('save', {state: 'start', message: gettext('Saving')});
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            global: false,
            success: function() { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            message = tryRefreshPageMessage;
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message = extractErrorMessage(jqXHR.responseText);
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    /**
     * Validate if 3PlayMedia options: fileId, apiKey.
     * @returns {boolean}
     */
    function validateThreePlayMediaConfig(data) {
        var message;
        var options = {
            type: 'POST',
            url: runtimeHandlers.validateThreePlayMediaConfig,
            dataType: 'json',
            data: JSON.stringify(data)
        };

        return $.ajax(
            options
        )
        .done(function(response) {
            message = response.message;
            if (!response.isValid) {
                runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
            }
        })
        .fail(function(jqXHR) {
            if (jqXHR.responseText) { // Try to get more specific error message we can show to user.
                message = extractErrorMessage(jqXHR.responseText);
            } else {
                message = tryRefreshPageMessage;
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    /**
     * Grab 3PlayMedia API configuration data.
     * @returns (object) 3PlayMedia's: apiKey + fileId
     */
    function getThreePlayMediaConfig() {
        var apiKey = $('#xb-field-edit-threeplaymedia_apikey', element).val();
        var fileId = $('#xb-field-edit-threeplaymedia_file_id', element).val();
        var streamingEnabled = $('#xb-field-edit-threeplaymedia_streaming', element).prop('selectedIndex');

        return {api_key: apiKey, file_id: fileId, streaming_enabled: !streamingEnabled};
    }

    $('.save-button', element).bind('click', function(event) {
        var validationSucceeded = false;
        event.preventDefault();

        $.when(validateThreePlayMediaConfig(getThreePlayMediaConfig())).then(
            function(response) {
                validationSucceeded = [
                    response.isValid,
                    validateTranscripts($langChoiceItem)
                ].every(Boolean);

                if (validationSucceeded) {
                    studioSubmit(fillValues(fields));
                }
            }
        );
    });

    $(element).find('.cancel-button').bind('click', function(event) {
        event.preventDefault();
        runtime.notify('cancel', {});
    });

    if (gotTranscriptsValue) {
        transcriptsValue = JSON.parse(gotTranscriptsValue);
    }

    transcriptsValue.forEach(function(transcriptValue) {
        disabledLanguages.push(transcriptValue.lang);
    });

    /**
     * Authenticate to video platform's API and show result message.
     */
    function authenticateVideoApi(data) {
        var message, status;

        $.ajax({
            type: 'POST',
            url: runtimeHandlers.authenticateVideoApi,
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(response) {
            var errorMessage = response.error_message;
            var successMessage = response.success_message;
            if (successMessage) {
                message = successMessage;
                status = SUCCESS;
                showBackendSettings();
            } else if (errorMessage) {
                message = errorMessage;
                status = ERROR;
            }
        })
        .fail(function(jqXHR) {
            message = tryRefreshPageMessage;
            status = ERROR;

            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message += extractErrorMessage(jqXHR.responseText);
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        })
        .always(function() {
            showStatus(
                $('.api-response.authenticate.status'),
                status,
                message
            );
        });
    }

    /**
     * Create a new transcript, containing valid data, after successful form submit.
     *
     * Arguments:
     *  event (jQuery.Event): Initial event provoked a form submitting.
     *  response (Object): Object containing information on an uploaded transcript and an upload status message.
     *  statusText (String): Information on an upload status (either "success" or "error").
     *  xhr (Object): XMLHttpRequest object.
     *  fieldName (String): String indicating type of uploaded subtitles (whether "transcripts" or "caption").
     *  lang (String): Subtitle language code (e.g. "uk").
     *  label (String): Subtitle language label (e.g. "Ukrainian").
     *  currentLiTag (Object): DOM element containing information on an uploaded subtitle.
     */
    function successHandler(event, response, statusText, xhr, fieldName, lang, label, currentLiTag) {
        var url = '/' + response.asset.id;
        // User can upload a file without extension
        var filename = $fileUploader[0].files[0].name;
        var downloadUrl = runtimeHandlers.downloadTranscript + '?' + url;
        var successMessage = gettext('File "{filename}" uploaded successfully').replace('{filename}', filename);
        var $parentDiv;
        var downloadUrlServer;
        var defaultTranscript;
        var isValidated = validateTranscriptFile(event, fieldName, filename, $fileUploader);
        var source = $fileUploader.data('source-manual');
        if (fieldName === 'handout' && isValidated) {
            $parentDiv = $('.file-uploader');
            $('.download-setting', $parentDiv).attr('href', downloadUrl).removeClass('is-hidden');
            $('a[data-change-field-name=' + fieldName + ']').text('Replace');
            showStatus($('.status', $parentDiv), SUCCESS, successMessage);
            $('input[data-field-name=' + fieldName + ']').val(url).change();
        } else if (fieldName === 'transcripts' && isValidated) {
            pushTranscript(lang, label, url, source, '', transcriptsValue);
            $('.add-transcript').removeClass('is-disabled');
            $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(transcriptsValue)).change();
            $(currentLiTag).find('.upload-transcript').text('Replace');
            $(currentLiTag).find('.download-transcript')
                .removeClass('is-hidden')
                .attr('href', downloadUrl);
            showStatus(
                $('.status', $(currentLiTag)),
                SUCCESS,
                successMessage
            );
            // Affect default transcripts: update a respective enabled transcript with an external url
            // of a newly created standard transcript
            downloadUrlServer =
                $('.list-settings-buttons .upload-setting.upload-transcript[data-lang-code=' + lang + ']')
                .siblings('a.download-transcript.download-setting').attr('href');
            defaultTranscript = {
                lang: lang,
                label: label,
                url: downloadUrlServer
            };
            createEnabledTranscriptBlock(defaultTranscript, downloadUrl);
            bindRemovalListenerEnabledTranscript(lang, label, downloadUrl);
        }
        // Reset data on a transcript, uploaded to a server
        $(event.currentTarget).attr({
            'data-change-field-name': '',
            'data-lang-code': '',
            'data-lang-label': ''
        });
    }

    /**
     * Wrap standard transcript removal sequence for it to be re-used.
     */
    function standardTranscriptRemovalWrapper(event) {
        // Affect default transcripts
        var $currentBlock = $(event.currentTarget).closest('li');
        var lang = $currentBlock.find('option:selected').val();
        var label = $currentBlock.find('option:selected').attr('data-lang-label');
        var defaultTranscript = {
            lang: lang,
            label: label,
            url: ''
        };
        // Affect standard transcripts
        removeTranscriptBlock(event, transcriptsValue, disabledLanguages);
        disableOption($langChoiceItem, disabledLanguages);
        removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        bindUploadListenerAvailableTranscript(lang, label);
    }

    $fileUploader.on('change', function(event) {
        var $currentTarget = $(event.currentTarget);
        var fieldName = $currentTarget.attr('data-change-field-name');
        var lang = $currentTarget.attr('data-lang-code');
        var label = $currentTarget.attr('data-lang-label');
        var currentLiTag = $('.language-transcript-selector')
            .children()[parseInt($currentTarget.attr('data-li-index'), 10)];
        if (!$fileUploader.val()) {
            return;
        }
        $('.upload-setting', element).addClass('is-disabled');
        $('.file-uploader-form', element).ajaxSubmit({
            success: function(response, statusText, xhr) {
                successHandler(event, response, statusText, xhr, fieldName, lang, label, currentLiTag);
            },
            error: function(jqXHR, textStatus) {
                runtime.notify('error', {title: gettext('Unable to update settings'), message: textStatus});
            }
        });
        $('.upload-setting', element).removeClass('is-disabled');
    });

    $videoApiAuthenticator.on('click', function(event) {
        var $data = $('.token', element).val();
        event.preventDefault();
        event.stopPropagation();
        authenticateVideoApi($data);
    });

    $('.lang-select').on('change', function(event) {
        languageChecker(event, transcriptsValue, disabledLanguages);
        disableOption($langChoiceItem, disabledLanguages);
        pushTranscriptsValue(transcriptsValue);
    });

    $('.upload-transcript, .upload-action').on('click', function(event) {
        clickUploader(event, $fileUploader);
    });

    $('.setting-clear').on('click', function(event) {
        var $currentBlock = $(event.currentTarget).closest('li');
        if ($('.file-uploader', $currentBlock).length > 0) {
            $('.upload-setting', $currentBlock).text('Upload');
            $('.download-setting', $currentBlock).addClass('is-hidden');
        }
        $currentBlock.find('ol').find('li:visible').remove();
    });

    $standardTranscriptUploader.click(function(event) {
        var $templateItem = $('.list-settings-item:hidden').clone();
        event.preventDefault();
        $(event.currentTarget).addClass('is-disabled');
        $templateItem.removeClass('is-hidden').appendTo($langChoiceItem);
        $('.upload-transcript', $templateItem).on('click', function(event) { // eslint-disable-line no-shadow
            clickUploader(event, $fileUploader);
        });
        $('.lang-select', $templateItem).on('change', function(event) { // eslint-disable-line no-shadow
            languageChecker(event, transcriptsValue, disabledLanguages);
            disableOption($langChoiceItem, disabledLanguages);
            pushTranscriptsValue(transcriptsValue);
        });
        // Bind a listener
        $('.remove-action').on('click', function(event) { // eslint-disable-line no-shadow
            standardTranscriptRemovalWrapper(event);
        });
    });

    $standardTranscriptRemover.click(function(event) {
        standardTranscriptRemovalWrapper(event);
    });

    $defaultTranscriptUploader.click(function(event) {
        var $currentTarget = $(event.currentTarget);
        var langCode = $currentTarget.attr('data-lang-code');
        var label = $currentTarget.attr('data-lang-label');
        var url = $currentTarget.attr('data-download-url');
        var source = $currentTarget.attr('data-source');
        var defaultTranscript = {
            lang: langCode,
            label: label,
            url: url,
            source: source
        };
        event.preventDefault();
        event.stopPropagation();
        currentLanguageCode = langCode;
        // Affect default transcripts
        uploadDefaultTranscriptsToServer(defaultTranscript);
        // Affect standard transcripts
        createTranscriptBlock(langCode, label, transcriptsValue, runtimeHandlers.downloadTranscript);
    });

    $defaultTranscriptRemover.click(function(event) {
        var $currentTarget = $(event.currentTarget);
        var langCode = $currentTarget.attr('data-lang-code');
        var langLabel = $currentTarget.attr('data-lang-label');
        var downloadUrl = $currentTarget.attr('data-download-url');
        var defaultTranscript = {
            lang: langCode,
            label: langLabel,
            url: downloadUrl
        };
        // Affect default transcripts
        removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        bindUploadListenerAvailableTranscript(langCode, langLabel);
        // Affect standard transcripts
        removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages);
        disableOption($langChoiceItem, disabledLanguages);
        event.preventDefault();
    });

    $defaultTranscriptsSwitcher.change(function() {
        $enabledLabel.toggleClass('is-hidden', $('.enabled-default-transcripts-section:visible').length);
        $availableLabel.toggleClass('is-hidden', $('.available-default-transcripts-section:visible').length);
    });
    // End of Raccoongang addons
}
