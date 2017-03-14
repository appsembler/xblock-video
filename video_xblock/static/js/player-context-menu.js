/**
 * This part is responsible for the player context menu.
 * Menu Options include:
 * - Play / Pause
 * - Mute / Unmute
 * - Fill browser / Unfill browser
 * - Speed
 *
 */

/**
 * Initialise player context menu with nested elements.
 */
domReady(function() {
    'use strict';
    var videoPlayer = document.getElementById(window.videoPlayerId);
    var dataSetup = JSON.parse(videoPlayer.getAttribute('data-setup'));
    var playbackRates = dataSetup.playbackRates;
    var docfrag = document.createDocumentFragment();
    // VideoJS Player() object necessary for context menu creation
    var player = videojs(window.videoPlayerId);

    /**
    * Cross-browser wrapper for element.matches
    * Source: https://gist.github.com/dalgard/7817372
    */
    function matchesSelector(domElement, selector) {
        var matchesSelector =              // eslint-disable-line no-shadow
            domElement.matches ||
            domElement.matchesSelector ||
            domElement.webkitMatchesSelector ||
            domElement.mozMatchesSelector ||
            domElement.msMatchesSelector ||
            domElement.oMatchesSelector;
        return matchesSelector.call(domElement, selector);
    }

    /**
    * Create elements of nested context submenu.
    */
    function createNestedContextSubMenu(e) {
        var target = e.target;
        var labelElement = target.innerText;
        var labelItem = getItem('speed').label; // eslint-disable-line no-use-before-define
        // Check conditions to be met for delegation of the popup submenu creation
        var menuItemClicked = matchesSelector(target, 'li.vjs-menu-item');
        var noSubmenuClicked = !target.querySelector('.vjs-contextmenu-ui-submenu');
        var menuItemsLabelsEqual = (labelElement === labelItem);
        // Generate nested submenu elements as document fragment
        var ulSubMenu = document.createElement('ul');
        // Wrap into conditional statement to avoid unnecessary variables initialization
        if (menuItemClicked && noSubmenuClicked) {
            var labelLength = labelElement.length;   // eslint-disable-line vars-on-top
            var lineFeedCode = 10;                   // eslint-disable-line vars-on-top
            // Check if the last character is an escaped one (line feed to get rid of)
            // which is the case for Microsoft Edge
            if (labelElement.charCodeAt(labelLength - 1) === lineFeedCode) {
                var labelElementSliced = labelElement.slice(0, -1);        // eslint-disable-line vars-on-top
                menuItemsLabelsEqual = (labelElementSliced === labelItem);
            }
        }
        ulSubMenu.className = 'vjs-contextmenu-ui-submenu';
        playbackRates.forEach(function(rate) {
            var liSubMenu = document.createElement('li');
            liSubMenu.className = 'vjs-submenu-item';
            liSubMenu.innerHTML = rate + 'x';
            ulSubMenu.appendChild(liSubMenu);
            liSubMenu.onclick = function() {
                player.playbackRate(parseFloat(rate));
            };
        });
        docfrag.appendChild(ulSubMenu);

        // Create nested submenu
        if (menuItemClicked && noSubmenuClicked && menuItemsLabelsEqual) {
            target.appendChild(docfrag);
        }
    }

    // Delegate creation of a nested submenu for a context menu
    videoPlayer.addEventListener('mouseover', createNestedContextSubMenu);

    // Create context menu options
    var content = [                         // eslint-disable-line vars-on-top
        {
            id: 'play',
            label: 'Play',
            listener: function() {
                var item = getItem('play');  // eslint-disable-line no-use-before-define
                if (player.paused()) {
                    player.play();
                    item.label = 'Pause';
                } else {
                    player.pause();
                    item.label = 'Play';
                }
            }
        }, {
            id: 'mute',
            label: 'Mute',
            listener: function() {
                var item = getItem('mute');  // eslint-disable-line no-use-before-define
                if (player.muted()) {
                    player.muted(false);
                    item.label = 'Mute';
                } else {
                    player.muted(true);
                    item.label = 'Unmute';
                }
            }
        }, {
            id: 'fullscreen',
            label: 'Fill browser',
            listener: function() {
                var item = getItem('fullscreen');  // eslint-disable-line no-use-before-define
                if (player.isFullscreen()) {
                    player.exitFullscreen();
                    item.label = 'Fill browser';
                } else {
                    player.requestFullscreen();
                    item.label = 'Unfill browser';
                }
            }
        }, {
            // Nested submenu creation is delegated to the player
            id: 'speed',
            label: 'Speed'
        }
    ];

    // Fire up vjs-contextmenu-ui plugin
    player.contextmenuUI({content: content});

    // Update context menu labels
    var getItem = (function(contextmenuUI) {  // eslint-disable-line vars-on-top
        var hash = {};
        contextmenuUI.content.forEach(function(item) {
            hash[item.id] = item;
        });
        return function(id) {
            return hash[id];
        };
    }(player.contextmenuUI));
});
