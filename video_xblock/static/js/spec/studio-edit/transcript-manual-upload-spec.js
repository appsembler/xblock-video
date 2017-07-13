/* global parseRelativeTime validateTranscripts getAllowedFileExtensions*/
/**
 * Tests for transcripts manual upload
 */

describe('Transcripts manual upload', function() {
    'use strict';
    it('return parseRelativeTime', function() {
        var tests = {
            0: '00:00:00',
            1234: '00:20:34',
            12345: '03:25:45',
            86399: '23:59:59',
            99999: '23:59:59',
            '-1': '00:00:00',
            '0:0:0': '00:00:00',
            '0:12:34': '00:12:34',
            '12:30': '00:12:30'
        };
        Object.keys(tests).forEach(function(value) {
            expect(parseRelativeTime(value)).toBe(tests[value]);
        });
    });

    it('returns getTranscriptUrl', function() {
        var transcriptsArray = [
            {
                lang: 'en',
                url: 'http://test.en/'
            },
            {
                lang: 'ru',
                url: 'http://test.ru/'
            }
        ];
        expect(getTranscriptUrl(transcriptsArray, 'en')).toBe('http://test.en/');
        expect(getTranscriptUrl(transcriptsArray, 'ru')).toBe('http://test.ru/');
        expect(getTranscriptUrl(transcriptsArray)).toBe('');
    });

    it('returns validateTranscripts', function() {
        var $testTranscriptsBlock;
        $('body').append('<ol id="test-transcript-block" class="list-settings language-transcript-selector">' +
            '<li class="list-settings-item">' +
            '<div class="list-settings-buttons">' +
            '<a href="#" class="download-transcript download-setting is-hidden">Download</a>' +
            '</div>' +
            '</li>' +
            '</ol>');

        $testTranscriptsBlock = $('#test-transcript-block');
        expect(validateTranscripts($testTranscriptsBlock)).toBeFalsy();
        $testTranscriptsBlock.first('li').find('.download-setting').removeClass('is-hidden');
        expect(validateTranscripts($testTranscriptsBlock)).toBeTruthy();
    });
});

describe('Correct file extensions are returned when', function() {
    'use strict';
    it('file is uploading in "transcripts" context', function() {
        expect(getAllowedFileExtensions('transcripts')).toEqual('.srt, .vtt');
    });

    it('file is uploading in other then "transcripts" context', function() {
        var handoutsAllowedFileTypes = (
        '.gif, .ico, .jpg, .jpeg, .png, .tif, .tiff, .bmp, .svg, ' +  // images
        '.pdf, .txt, .rtf, .csv, ' +                                  // documents
        '.doc, .docx, .xls, .xlsx, .ppt, .pptx, .pub, ' +             // MSOffice
        '.odt, .ods, .odp, ' +                                        // openOffice
        '.zip, .7z, .gzip, .tar ' +                                   // archives
        '.html, .xml, .js, .sjson'                                    // other
    );
        expect(getAllowedFileExtensions('somethings_else_or_null')).toEqual(handoutsAllowedFileTypes);
    });
});
