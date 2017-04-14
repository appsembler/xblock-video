/* global fillValues */
/**
 * Tests for studio edit's utils
 */
describe('Studio edit utils', function() {
    'use strict';
    var fields = [
        {
            name: 'display_name',
            isSet: function() { return true; },
            val: function() { return 'test value'; }
        },
        {
            name: 'href',
            isSet: function() { return false; }
        }
    ];
    it("return field's fillValues", function() {
        expect(fillValues(fields)).toEqual({values: {display_name: 'test value'}, defaults: ['href']});
    });
    it('return showStatus', function() {
        var $testStatusBlock;
        $('body').append('<div id="test-status-block" class="is-hidden"></div>');
        $testStatusBlock = $('#test-status-block');
        showStatus($testStatusBlock, 'success', 'test message');
        expect($testStatusBlock.text()).toBe('test message');
        expect($testStatusBlock.hasClass('status-success')).toBeTruthy();
        expect($testStatusBlock.hasClass('is-hidden')).toBeFalsy();
        setTimeout(function() {
            // status block should be hidden in 5 seconds
            expect($testStatusBlock.hasClass('is-hidden')).toBeTruthy();
        }, 5001);
    });
});

