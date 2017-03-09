/**
    Set up the Video xblock studio editor. This part is responsible for validation and sending of the data to a backend.
    Reference:
        https://github.com/edx/xblock-utils/blob/v1.0.3/xblockutils/templates/studio_edit.html
*/
function StudioEditableXBlock(runtime, element) {
    'use strict';

    var fields = [];
    // Studio includes a copy of tinyMCE and its jQuery plugin
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined');  // TODO: Remove TinyMCE
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin
    var $defaultTranscriptsSwitcher = $('input.default-transcripts-switch-input');
    var $enabledLabel = $('div.custom-field-section-label.enabled-transcripts');
    var $availableLabel = $('div.custom-field-section-label.available-transcripts');
    var noEnabledTranscript;
    var noAvailableTranscript;
    var $modalHeaderTabs = $('.editor-modes.action-list.action-modes');
    var currentTabName;
    var isNotDummy = $('#xb-field-edit-href').val() !== '';
    var SUCCESS = 'success';
    var ERROR = 'error';


    /** Toggle studio editor's current tab.
     */
    function toggleEditorTab(tabName) {
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
                toggleEditorTab(currentTabName);
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

    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        var contextId = $wrapper.context.id;
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean') {  // eslint-disable-line
                    return (val == 'true' || val == '1');  // eslint-disable-line
                }
                if (type == 'integer') {  // eslint-disable-line
                    return parseInt(val, 10);
                }
                if (type == 'float') {  // eslint-disable-line
                    return parseFloat(val);
                }
                if (type == 'generic' || type == 'list' || type == 'set') {  // eslint-disable-line
                    val = val.trim();
                    if (val === '') {
                        val = null;
                    } else {
                        val = JSON.parse(val); // TODO: handle parse errors
                    }
                    return val;
                }
                /* eslint-disable */
                if (type == 'string' && (
                    contextId == 'xb-field-edit-start_time'
                    || contextId == 'xb-field-edit-end_time')) {
                    return parseRelativeTime(val);
                }
                /* eslint-disable */
                return val;
            },
            removeEditor: function() {
                $field.tinymce().remove();
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $field.bind('change input paste', fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
            // Remove all enabled default transcripts
            removeAllEnabledTranscripts(initialDefaultTranscriptsData, bindUploadListenerAvailableTranscript);
        });
        if (type == 'html' && tinyMceAvailable) {
            tinyMCE.baseURL = baseUrl + '/js/vendor/tinymce/js/tinymce';
            $field.tinymce({
                theme: 'modern',
                skin: 'studio-tmce4',
                height: '200px',
                formats: { code: { inline: 'code' } },
                codemirror: { path: '' + baseUrl + '/js/vendor' },
                convert_urls: false,
                plugins: 'link codemirror',
                menubar: false,
                statusbar: false,
                toolbar_items_size: 'small',
                toolbar: 'formatselect | styleselect | bold italic underline forecolor wrapAsCode | bullist numlist outdent indent blockquote | link unlink | code',
                resize: 'both',
                setup : function(ed) {
                    ed.on('change', fieldChanged);
                }
            });
        }

        if (type == 'datepicker' && datepickerAvailable) {
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: 'm/d/yy'});
        }
    });

    $(element).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };

        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return false; },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($(this).val()));
                    }
                });
                return val;
            }
        });
        $checkboxes.bind('change input', fieldChanged);

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

    /**
     * Is there a more specific error message we can show?
     * @param  {String} responseText JSON received from ajax call
     * @return {String}              Error message extracted from input JSON or a portion of input text
     */
    function extractErrorMessage(responseText) {
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
    /** Submit studio editor settings.
     */
    function studio_submit(data) {
        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext('Saving')});
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.');
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message = extractErrorMessage(jqXHR.responseText);
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    // Raccoongang changes
    $('.save-button', element).bind('click', function(event) {
        var isValidated = validateTranscripts(event, $langChoiceItem);
        if (isValidated) {
            var values = fillValues(fields);
            studio_submit(values);
        }
    });

    $(element).find('.cancel-button').bind('click', function(event) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        event.preventDefault();
        runtime.notify('cancel', {});
    });
    // End of Raccoongang changes

    // Raccoongang addons
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
    var downloadTranscriptHandlerUrl = runtime.handlerUrl(element, 'download_transcript');
    var authenticateVideoApiHandlerUrl = runtime.handlerUrl(element, 'authenticate_video_api_handler');
    var uploadDefaultTranscriptHandlerUrl = runtime.handlerUrl(element, 'upload_default_transcript_handler');
    var currentLanguageCode;
    var currentLanguageLabel;
    var initialDefaultTranscriptsData = getInitialDefaultTranscriptsData();
    var initialDefaultTranscripts = initialDefaultTranscriptsData[0];

    if (gotTranscriptsValue) {
        transcriptsValue = JSON.parse(gotTranscriptsValue);
    }

    transcriptsValue.forEach(function(transcriptValue) {
        disabledLanguages.push(transcriptValue.lang)
    });

    /**
     * Authenticate to video platform's API and show result message.
     */
    function authenticateVideoApi(data) {
        var message, status;

        $.ajax({
            type: 'POST',
            url: authenticateVideoApiHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(response) {
            var error_message = response['error_message'];
            var success_message = response['success_message'];
            if (success_message) {
                message = success_message;
                status = SUCCESS;
                showBackendSettings();
            }
            else if (error_message) {
                message = error_message;
                status = ERROR;
            };
        })
        .fail(function(jqXHR) {
            message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            status = ERROR;

            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message += extractErrorMessage(jqXHR.responseText);
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        })
        .always(function() {
            showStatus(
                message,
                status,
                $('.api-response.authenticate.status')
            );
        });
    }

    /**
     * Upload a transcript available on a video platform to video xblock and update displayed default transcripts.
     */
    function uploadDefaultTranscriptsToServer(data) {
        var message, status;

        $.ajax({
            type: 'POST',
            url: uploadDefaultTranscriptHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(response) {
            var newLang = response['lang'];
            var newLabel = response['label'];
            var newUrl = response['url'];
            // Create a standard transcript
            pushTranscript(newLang, newLabel, newUrl, '', transcriptsValue);
            pushTranscriptsValue(transcriptsValue);
            // Add a default transcript to the list of enabled ones
            var downloadUrl = downloadTranscriptHandlerUrl + '?' + newUrl;
            var defaultTranscript= {'lang': newLang, 'label': newLabel, 'url': downloadUrl};
            createEnabledTranscriptBlock(defaultTranscript, downloadUrl);
            bindRemovalListenerEnabledTranscript(newLang, newLabel, newUrl);
            // Display status messages
            // var error_message = response['error_message'];
            message = response['success_message'];
            status = SUCCESS;
        })
        .fail(function(jqXHR) {
            message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                message += extractErrorMessage(jqXHR.responseText);
            }
            status = ERROR;
        })
        .always(function() {
            showStatus(
                message,
                status,
                $('.api-response.upload-default-transcript.' + currentLanguageCode + '.status')
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
        var url = '/' + response['asset']['id'];
        // User can upload a file without extension
        var filename = $fileUploader[0].files[0].name;
        var downloadUrl = downloadTranscriptHandlerUrl + '?' + url;
        var successMessage = 'File "' + filename + '" uploaded successfully';
        var $parentDiv;
        var downloadUrlServer;
        var defaultTranscript;
        var isValidated = validateTranscriptFile(event, fieldName, filename, $fileUploader);
        if (fieldName == 'handout' && isValidated) {
            $parentDiv = $('.file-uploader');
            $('.download-setting', $parentDiv).attr('href', downloadUrl).removeClass('is-hidden');
            $('a[data-change-field-name=' + fieldName + ']').text('Replace');
            displayStatusCaptions(SUCCESS, successMessage, $parentDiv);
            $('input[data-field-name=' + fieldName + ']').val(url).change();
        } else if (fieldName == 'transcripts' && isValidated) {
            pushTranscript(lang, label, url, '', transcriptsValue);
            $('.add-transcript').removeClass('is-disabled');
            $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(transcriptsValue)).change();
            $(currentLiTag).find('.upload-transcript').text('Replace');
            $(currentLiTag).find('.download-transcript')
                .removeClass('is-hidden')
                .attr('href', downloadUrl);
            displayStatusTranscripts(SUCCESS, successMessage, currentLiTag);
            // Affect default transcripts: update a respective enabled transcript with an external url
            // of a newly created standard transcript
            downloadUrlServer =
                $('.list-settings-buttons .upload-setting.upload-transcript[data-lang-code=' + lang + ']')
                .siblings('a.download-transcript.download-setting').attr('href');
            defaultTranscript = {'lang': lang, 'label': label, 'url': downloadUrlServer};
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
     * Bind upload listener to a newly created available transcript.
     */
    function bindUploadListenerAvailableTranscript(langCode, langLabel) {
        var $uploadElement = $('.default-transcripts-action-link.upload-default-transcript[data-lang-code=' + langCode + ']');
        $uploadElement.click(function () {
            // Get url for a transcript fetching from the API
            var downloadUrlApi = getTranscriptUrl(initialDefaultTranscripts, langCode);
            var defaultTranscript = {'lang': langCode, 'label': langLabel, 'url': downloadUrlApi};
            uploadDefaultTranscriptsToServer(defaultTranscript);
            // Affect standard transcripts
            createTranscriptBlock(langCode, langLabel, transcriptsValue, downloadTranscriptHandlerUrl);
        });
    }

    /**
     * Bind removal listener to a newly created enabled transcript.
     */
    function bindRemovalListenerEnabledTranscript(langCode, langLabel, downloadUrlServer) {
        var $removeElement = $('.default-transcripts-action-link.remove-default-transcript[data-lang-code=' + langCode + ']');
        $removeElement.click(function(event) {
            var defaultTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrlServer};
            // Affect default transcripts
            removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            bindUploadListenerAvailableTranscript(langCode, langLabel);
            // Affect standard transcripts
            removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages);
            disableOption($langChoiceItem, disabledLanguages);
            event.preventDefault();
        });
    }

    /**
     * Wrap standard transcript removal sequence for it to be re-used.
     */
    function standardTranscriptRemovalWrapper(event) {
        // Affect standard transcripts
        removeTranscriptBlock(event, transcriptsValue, disabledLanguages);
        disableOption($langChoiceItem, disabledLanguages);
        // Affect default transcripts
        var $currentBlock = $(event.currentTarget).closest('li');
        var lang = $currentBlock.find('option:selected').val();
        var label = $currentBlock.find('option:selected').attr('data-lang-label');
        var defaultTranscript = {'lang' : lang, 'label' : label, 'url': ''};
        removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        bindUploadListenerAvailableTranscript(lang, label);
    }

    $fileUploader.on('change', function(event) {
        if (!$fileUploader.val()) {
            return;
        }
        var fieldName = $(event.currentTarget).attr('data-change-field-name');
        var lang = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var currentLiIndex = $(event.currentTarget).attr('data-li-index');
        var currentLiTag = $('.language-transcript-selector').children()[parseInt(currentLiIndex)];
        $('.upload-setting', element).addClass('is-disabled');
        $('.file-uploader-form', element).ajaxSubmit({
            success: function(response, statusText, xhr) {
                successHandler(event, response, statusText, xhr, fieldName, lang, label, currentLiTag)
            },
            error: function(jqXHR, textStatus, errorThrown) {
                runtime.notify('error', {title: gettext('Unable to update settings'), message: textStatus});
            }
        });
        $('.upload-setting', element).removeClass('is-disabled');
    });

    $videoApiAuthenticator.on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var $data = $('.token', element).val();
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

    $('.setting-clear').on('click', function (event) {
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
        $('.upload-transcript', $templateItem).on('click', function(event) {
            clickUploader(event, $fileUploader);
        });
        $('.lang-select', $templateItem).on('change', function(event) {
            languageChecker(event, transcriptsValue, disabledLanguages);
            disableOption($langChoiceItem, disabledLanguages);
            pushTranscriptsValue(transcriptsValue);
        });
        // Bind a listener
        $('.remove-action').on('click', function(event) {
            standardTranscriptRemovalWrapper(event);
        });
   });

    $standardTranscriptRemover.click(function(event) {
        standardTranscriptRemovalWrapper(event);
    });

    $defaultTranscriptUploader.click(function(event) {
        event.preventDefault();
        event.stopPropagation();
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var url = $(event.currentTarget).attr('data-download-url');
        currentLanguageCode = langCode;
        currentLanguageLabel = label;
        var defaultTranscript = {'lang': langCode, 'label' : label, 'url' : url};
        // Affect default transcripts
        uploadDefaultTranscriptsToServer(defaultTranscript);
        // Affect standard transcripts
        createTranscriptBlock(langCode, label, transcriptsValue, downloadTranscriptHandlerUrl)
    });

    $defaultTranscriptRemover.click(function(event) {
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var langLabel = $(event.currentTarget).attr('data-lang-label');
        var downloadUrl = $(event.currentTarget).attr('data-download-url');
        var defaultTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrl};
        // Affect default transcripts
        removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
        bindUploadListenerAvailableTranscript(langCode, langLabel);
        // Affect standard transcripts
        removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages);
        disableOption($langChoiceItem, disabledLanguages);
        event.preventDefault();
    });

    $defaultTranscriptsSwitcher.change(function(){
        noEnabledTranscript = !$('.enabled-default-transcripts-section:visible').length;
        noAvailableTranscript = !$('.available-default-transcripts-section:visible').length;
        // Hide label of enabled default transcripts block if no transcript is enabled on video xblock, and vice versa
        setDisplayDefaultTranscriptsLabel(noEnabledTranscript, $enabledLabel);
        // Hide label of available default transcripts block if no transcript is available on a platform, and vice versa
        setDisplayDefaultTranscriptsLabel(noAvailableTranscript, $availableLabel);
    });
    // End of Raccoongang addons
}
