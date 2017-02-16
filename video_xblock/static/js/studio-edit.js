/**
    StudioEditableXBlock function for setting up the Video xblock.
    This function was copied from xblock-utils by link
        https://github.com/edx/xblock-utils/blob/master/xblockutils/templates/studio_edit.html
    and extended by Raccoon Gang company
    It is responsible for a validating and sending data to backend
*/
function StudioEditableXBlock(runtime, element) {
    'use strict';

    var fields = [];
    // Studio includes a copy of tinyMCE and its jQuery plugin
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined');  // TODO: Remove TinyMCE
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

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
        });
    });

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
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(', ');
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
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

    $(element).find('.cancel-button').bind('click', function(e) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        e.preventDefault();
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
        $.ajax({
            type: 'POST',
            url: authenticateVideoApiHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(response) {
                var error_message = response['error_message'];
                var success_message = response['success_message'];
                if (success_message) {
                    showStatus(
                        success_message,
                        'success',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error');
                    showBackendSettings();
                }
                else if (error_message) {
                    showStatus(
                        error_message,
                        'error',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error');
                }
            }
        })
        .fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            showStatus(
                message,
                'error',
                '.api-request.authenticate.status-success',
                '.api-request.authenticate.status-error'
            );
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(', ');
                        showStatus(
                            message,
                            'error',
                            '.api-request.authenticate.status-success',
                            '.api-request.authenticate.status-error'
                        );                   }
                } catch (error) {
                    message = jqXHR.responseText.substr(0, 300);
                    showStatus(
                        message,
                        'error',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error'
                    );
                }
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    /**
     * Upload a transcript available on a video platform to video xblock and update displayed default transcripts.
     */
    function uploadDefaultTranscriptsToServer(data) {
        $.ajax({
            type: 'POST',
            url: uploadDefaultTranscriptHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(response) {
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
                var success_message = response['success_message'];
                if (success_message) {
                    showStatus(
                        success_message,
                        'success',
                        '.api-request.upload-default-transcript.' + newLang + '.status-success',
                        '.api-request.upload-default-transcript.' + newLang + '.status-error');
                }
            }
        })
        .fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            showStatus(
                message,
                'error',
                '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
            );
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(', ');
                        showStatus(
                            message,
                            'error',
                            '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                            '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
                        );                   }
                } catch (error) {
                    message = jqXHR.responseText.substr(0, 300);
                    showStatus(
                        message,
                        'error',
                        '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                        '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
                    );
                }
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    /**
     * Create new transcript, containing valid data, after successful form submit.
     */
    function successHandler(response, statusText, xhr, fieldName, lang, label, currentLiTag) {
        var url = '/' + response['asset']['id'];
        var regExp = /.*@(.+\..+)/;
        var filename = regExp.exec(url)[1];
        var downloadUrl = downloadTranscriptHandlerUrl + '?' + url;
        if (fieldName == 'handout') {
            var $parentDiv = $('.file-uploader', element);
            $('.download-setting', $parentDiv).attr('href', downloadUrl).removeClass('is-hidden');
            $('a[data-change-field-name=' + fieldName + ']').text('Replace');
            showUploadStatus($parentDiv, filename);
            $('input[data-field-name=' + fieldName + ']').val(url).change();
        } else {
            pushTranscript(lang, label, url, '', transcriptsValue);
            $('.add-transcript').removeClass('is-disabled');
            $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(transcriptsValue)).change();
            $(currentLiTag).find('.upload-transcript').text('Replace');
            $(currentLiTag).find('.download-transcript')
                .removeClass('is-hidden')
                .attr('href', downloadUrl);
            showUploadStatus($(currentLiTag), filename);
            // Affect default transcripts
            // Update respective enabled transcript with an external url from a newly created standard transcript
            var downloadUrlServer = $('.list-settings-buttons .upload-setting.upload-transcript[data-lang-code=' + lang + ']')
                .siblings('a.download-transcript.download-setting').attr('href');
            var defaultTranscript= {'lang': lang, 'label': label, 'url': downloadUrlServer};
            createEnabledTranscriptBlock(defaultTranscript, downloadUrl);
            bindRemovalListenerEnabledTranscript(lang, label, downloadUrl);
        }
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
        var $uploadElement = $('.default-transcripts-action-link.upload-default-transcript:visible[data-lang-code=' + langCode + ']');
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
        var $removeElement = $('.default-transcripts-action-link.remove-default-transcript:visible[data-lang-code=' + langCode + ']');
        $removeElement.click(function() {
            var defaultTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrlServer};
            // Affect default transcripts
            removeEnabledTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData);
            bindUploadListenerAvailableTranscript(langCode, langLabel);
            // Affect standard transcripts
            removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages);
            disableOption($langChoiceItem, disabledLanguages);
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
                successHandler(response, statusText, xhr, fieldName, lang, label, currentLiTag)
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
    });
    // End of Raccoongang addons
}
