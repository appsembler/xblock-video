function StudioEditableXBlock(runtime, element) {
    "use strict";

    var fields = [];
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean')
                    return (val == 'true' || val == '1');
                if (type == "integer")
                    return parseInt(val, 10);
                if (type == "float")
                    return parseFloat(val);
                if (type == "generic" || type == "list" || type == "set") {
                    val = val.trim();
                    if (val === "")
                        val = null;
                    else
                        val = JSON.parse(val); // TODO: handle parse errors
                }
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
        $field.bind("change input paste", fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
        if (type == 'html' && tinyMceAvailable) {
            tinyMCE.baseURL = baseUrl + "/js/vendor/tinymce/js/tinymce";
            $field.tinymce({
                theme: 'modern',
                skin: 'studio-tmce4',
                height: '200px',
                formats: { code: { inline: 'code' } },
                codemirror: { path: "" + baseUrl + "/js/vendor" },
                convert_urls: false,
                plugins: "link codemirror",
                menubar: false,
                statusbar: false,
                toolbar_items_size: 'small',
                toolbar: "formatselect | styleselect | bold italic underline forecolor wrapAsCode | bullist numlist outdent indent blockquote | link unlink | code",
                resize: "both",
                setup : function(ed) {
                    ed.on('change', fieldChanged);
                }
            });
        }

        if (type == 'datepicker' && datepickerAvailable) {
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: "m/d/yy"});
        }
    });

    $(element).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');

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
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $checkboxes.bind("change input", fieldChanged);

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

    var studio_submit = function(data) {
        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    // Raccoongang changes

    var fillValues = function (e) {
        var values = {};
        var notSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
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
        studio_submit({values: values, defaults: notSet});
    };

    var validateTranscripts = function(e){
        e.preventDefault();
        var isValid = [];
        var $visibleLangChoiceItems = $langChoiceItem.find('li:visible');
        $visibleLangChoiceItems.each(function(idx, el){
            var urls = $('.download-setting', $(el)).filter('.is-hidden');
            if (urls.length){
                $('.status-error', $(el))
                    .text('Please upload the transcript file for this language or remove the language.')
            } else {
                isValid.push(1)
            }
        });
        if (isValid.length == $visibleLangChoiceItems.length){
            fillValues(e)
        }
    };

    $('.save-button', element).bind('click', validateTranscripts);

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
    var $langChoiceItem = $('.language-transcript-selector', element);
    var gotTranscriptsValue = $('input[data-field-name="transcripts"]').val();

    if (gotTranscriptsValue){
        transcriptsValue = JSON.parse(gotTranscriptsValue);
    }

    transcriptsValue.forEach(function(transcriptValue, index, array) {
        disabledLanguages.push(transcriptValue.lang)
    });

    var disableOption = function(){

        $langChoiceItem.find('option').each(function(ind){
            if (disabledLanguages.indexOf($(this).val()) > -1){
                $(this).attr('disabled', true)
            } else {
                $(this).attr('disabled', false)
            }
        })
    };

    var pushTranscript = function (lang, label, url){
        var indexLanguage;
        for (var i=0; i < transcriptsValue.length; i++){
            if (lang == transcriptsValue[i].lang){
                indexLanguage = i;
                break;
            }
        }
        if (indexLanguage !== undefined){
            transcriptsValue[indexLanguage].url = url
        } else {
            transcriptsValue.push({
                lang: lang,
                url: url,
                label: label
            })
        }
        $('.add-transcript').removeClass('is-disabled');
    };

    var clickUploader = function(event){
        event.preventDefault();
        event.stopPropagation();
        var $buttonBlock = $(event.currentTarget);
        var indexOfParentLi = $('.language-transcript-selector').children().index($buttonBlock.closest('li'));
        $fileUploader.attr({
            'data-lang-code': $buttonBlock.attr('data-lang-code'),
            'data-lang-label': $buttonBlock.attr('data-lang-label'),
            'data-change-field-name': $buttonBlock.attr('data-change-field-name'),
            'accept': $buttonBlock.attr('data-change-field-name') == 'transcripts' ? '.srt, .vtt' : '',
            'data-li-index': $buttonBlock.attr('data-change-field-name') == 'transcripts' ? indexOfParentLi : ''
        });

        $fileUploader.click();
    };

    var languageChecker = function (event) {
        event.stopPropagation();
        var $selectedOption = $(event.currentTarget).find('option:selected');
        var selectedLanguage = $selectedOption.val();
        var languageLabel = $selectedOption.attr('data-lang-label');
        var $langSelectParent = $(event.currentTarget).parent('li');
        var $uploadButton = $('.upload-transcript', $langSelectParent);
        var oldLang = $uploadButton.data('lang-code');
        if (selectedLanguage != oldLang && selectedLanguage != ''){
            pushTranscript(selectedLanguage, languageLabel, '');
            disabledLanguages.push(selectedLanguage);
            if (oldLang != ''){
                removeTranscript(oldLang);
                removeLanguage(oldLang);
            }
            $uploadButton.data('lang-code', selectedLanguage);
        } else if (selectedLanguage == '') {
            $selectedOption.val($uploadButton.data('lang-code'));
            $('.remove-action', $langSelectParent).trigger('click');
        }
        $uploadButton.attr({
            'data-lang-code': selectedLanguage,
            'data-lang-label': languageLabel
        });
        $uploadButton.removeClass('is-hidden').text('Upload');
        disableOption();
        pushTranscriptsValue();
    };

    var removeLanguage = function(language){
        var index = disabledLanguages.indexOf(language);
        disabledLanguages.splice(index, 1);
    };

    var removeTranscript = function(lang){
        for (var i=0; i < transcriptsValue.length; i++){
            if (lang == transcriptsValue[i].lang){
                transcriptsValue.splice(i,1);
                break;
            }
        }
    };

    var pushTranscriptsValue = function(){
        transcriptsValue.forEach(function (transcriptValue, index, array){
            if (transcriptValue.lang == "" || transcriptValue.label == "" || transcriptValue.url == ""){
                transcriptsValue.splice(index, 1);
            }
        });
        $('input[data-field-name="transcripts"]').val(JSON.stringify(transcriptsValue)).change();
    };

    var removeTranscriptBlock = function(event){
        event.preventDefault();
        event.stopPropagation();
        var $currentBlock = $(event.currentTarget).closest('li');
        var lang = $currentBlock.find('option:selected').val();
        removeTranscript(lang);
        if (!transcriptsValue.length){
            $currentBlock.parents('li').removeClass('is-set').find('.setting-clear').removeClass('active').addClass('inactive');
        }
        removeLanguage(lang);
        pushTranscriptsValue();
        $('.add-transcript', element).removeClass('is-disabled');
        $currentBlock.remove();
        disableOption();

    };

    var showUploadStatus = function($element, filename){
        $('.status-error', $element).empty();
        $('.status-upload', $element).text('File ' + '"' + filename + '"' + ' uploaded successfully').show();
        setTimeout(function(){
            $('.status-upload', $element).hide()
        }, 5000);
    };

    var successHandler = function(response, statusText, xhr, fieldName, lang, label, currentLiTag) {
        var url = '/' + response['asset']['id'];
        var regExp = /.*@(.+\..+)/;
        var filename = regExp.exec(url)[1];
        if (fieldName == "handout"){
            var $parentDiv = $('.file-uploader', element);
            $('.download-setting', $parentDiv).attr({'href': url, 'download': filename}).removeClass('is-hidden');
            $('a[data-change-field-name=' + fieldName + ']').text('Replace');
            showUploadStatus($parentDiv, filename);
            $('input[data-field-name=' + fieldName + ']').val(url).change();
        } else {
            pushTranscript(lang, label, url);
            $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(transcriptsValue)).change();
            $(currentLiTag).find('.upload-transcript').text('Replace');
            $(currentLiTag).find('.download-transcript')
                .removeClass('is-hidden')
                .attr({'href': url, 'download': filename});
            showUploadStatus($(currentLiTag), filename);
        }
        $(event.currentTarget).attr({
            'data-change-field-name': '',
            'data-lang-code': '',
            'data-lang-label': ''
        });
    };

    $fileUploader.on('change', function(event) {
        if (!$fileUploader.val()){
            return;
        };
        var fieldName = $(event.currentTarget).attr('data-change-field-name');
        var lang = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var currentLiIndex = $(event.currentTarget).attr('data-li-index');
        var currentLiTag = $('.language-transcript-selector').children()[parseInt(currentLiIndex)];
        $('.upload-setting', element).addClass('is-disabled');
        $('.file-uploader-form', element).ajaxSubmit({
            success: function(response, statusText, xhr){
                successHandler(response, statusText, xhr, fieldName, lang, label, currentLiTag)
            },
            error: function(jqXHR, textStatus, errorThrown){
                runtime.notify('error', {title: gettext("Unable to update settings"), message: textStatus});
            }
        });
        $('.upload-setting', element).removeClass('is-disabled');
    });

    $('.add-transcript', element).on('click', function (event) {
        event.preventDefault();
        $(event.currentTarget).addClass('is-disabled');
        var $templateItem = $('.list-settings-item:hidden').clone();
        $templateItem.removeClass('is-hidden').appendTo($langChoiceItem);
        $('.upload-transcript', $templateItem).on('click', clickUploader);
        $('.lang-select', $templateItem).on('change', languageChecker);
        $('.remove-action', element).on('click', removeTranscriptBlock);
    });

    $('.lang-select').on('change', languageChecker);

    $('.upload-transcript, .upload-action', element).on('click', clickUploader);

    $('.remove-action', element).on('click', removeTranscriptBlock);

    $('.setting-clear').on('click', function (event){
        var $currentBlock = $(event.currentTarget).closest('li');
        if ($('.file-uploader', $currentBlock).length > 0){
            $('.upload-setting', $currentBlock).text('Upload');
            $('.download-setting', $currentBlock).addClass('is-hidden');
        }
        $currentBlock.find('ol').find('li:visible').remove();
    });
    $().ready(function(){
        disableOption();
    });
    // End of Raccoongang addons
}
