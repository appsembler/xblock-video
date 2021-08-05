# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.0.0-community-alpha] - 2021-08-05

### Added

- Partial Py3/Juniper compat updates, not backward compat to Python 2.

## [0.10.7] - 2021-08-05

### Fixed

- Don't override account_id with a blank form value for new XBlock instances when value available from settings

## [0.10.6] - 2021-08-05

### Fixed

- Fix BrightCove styling for players based on video.js v6+ (breaks video.js5 but that's very old now)
- a11y fix - title on video iframe

## [0.10.5] - 2021-08-05

Released 2021-08-05, fix commit was made 2021-04-19

### Fixed

-  Added mute before playing video for chrome to avoid autoplay policy restriction

## [0.10.4] - 2021-08-05

Released 2021-08-05, fix commit on 2020-09-18

### Fixed

- Fixed rendering of Django templates fails in Ironwood after a video_xblock is rendered

## [0.10.3] - 2018-11-22

### Added

- Fixes for Hawthorn

## [0.10.2] - 2018-07-04

### Fixes

- Fixed list of components installed by pip install

## [0.10.1] - 2018-02-13

### Added

- Multiple transcripts downloading;
- Error handling during Brightcove video re-transcode job submitting;

### Fixed

- Safari `empty transcripts` issue;
- Studio editor improvements:
    - transcripts accordion switch;
    - re-transcode button styling;

## [0.10.0] - 2018-01-24

### Added

- Ability to perform search within text tracks (subtitles/transcripts);

### Fixed

- Player controls alignment;
- Active languages highlighting inconsistency between transcript and caption menus;

## [0.9.4] - 2018-01-18

### Fixed

- Language menu popup behaviour in player's subtitles/transcripts control group;
- Removed caret control from controls;
- Speed rates popup shifted;

## [0.9.3] - 2017-12-28

### Fixed

- Removed menu popup doubling in player's subtitles/transcripts control group.
- Updated python code quality configuration.

## [0.9.2] - 2017-11-03

### Fixed

- Edge / IE11 issues;
- Brightcove player ver. 6 layout:

>Brightcove player version 6 (videojs v.6 based) has introduced new css-styles and some decent API changes.

## [0.9.1] - 2017-08-04

### Changed

- Handouts: wide list of file types now is allowed to upload (please,
 refer to README file).
- UI: minor changes to default transcripts accordion section (appearance, wordings)
- Increase test coverage to improve product stability.
- Some code base refactoring to make xblock more robust.

### Fixed

- Brightcove player state handling
- Token field regression bug (accordion refactoring)

## [0.9.0] - 2017-07-11

### Added

- Direct transcripts streaming from 3PlayMedia service.
  Now Video Xblock will always use up-to-date transcripts from 3PM.

### Changed

- UI: Transcripts settings section now split into two panels.
  To make more apparent how different options are related and which
  transcripts are going to be diplayed.
  - "Manual & default transcripts"
  - "3PlayMedia transcripts"

## [0.8.0] - 2017-06-30

### Added

- Vimeo: default transcripts fetching.

## Changed

- Use new 3PlayMedia API to fetch transcripts translations.
- Increase test coverage. Which means better stability.

### Fixed

- Bug preventing setting Video Platform API key. E.g. `BC_TOKEN` for Brightcove.
- Transcripts collision bug, which prevented teachers to replace
  transcript for a given language.

## [0.7.1] - 2017-05-18

### Added

- Pass some debugging information to the front end.

## [0.7.0] - 2017-05-17

### Added

- XBlock SDK Workbench scenarios to simplify development.
- Acceptance tests on top of XBlock SDK Workbench.

### Removed

- Removed TravisCI integration.

## [0.6.6] - 2017-05-03

### Changed

- Make transcripts help hint more helpful.

## [0.6.5] - 2017-04-21

### Added

- Bundle VideoJS fonts into Video XBlock.

## [0.6.4] - 2017-04-14

### Changed

- Improve video player controls look&feel.
- Make subtitles responsive.

### Fixed

- Fetching subtitles from 3PlayMedia.

## [0.6.3] - 2017-03-30

### Changed

- Extend Brightcove url regex to include additional set of video urls.
  Now it supports both:
  - `https://studio.brightcove.com/products/videos/<media-id>`
  - `https://studio.brightcove.com/products/videocloud/media/videos/<media-id>`
- Restructure JavaScript codebase.

## [0.6.2] - 2017-03-27

### Changed

- Update `videojs-wistia` external JS dependency.

## [0.6.1] - 2017-03-27

### Changed

- Simplify VideoXBlock installation by bundling JS/CSS dependencies into
  `static/vendor` subdirectory.

## [0.6.0] - 2017-03-23

### Added

- 3PlayMedia support. Now you can fetch transcripts for your video from 3PM.
- Open edX settings support. Now administrators can set default values
  for VideoXBlock on a system-wide level.

### Changed

- Swith from Coveralls to Codecov for better code coverage.
- Interactive transcripts now align current line to the middle of video frame.

### Fixed

- Interactive transcripts automscrolling for Brightcove videos.

## [0.5.0] - 2017-03-14

### Added

- Html5 video support.
- Manual uploaded transcripts validation: file extension and size.
- Code stabilization:
  - Python unit tests.
  - JS unit tests foundation.

### Changed

- Interactive transcripts now automatically scroll to follow video.
- UI improvements in Studio:
  - Split Video XBlock settings into Basic & Advanced tabs.
  - Display only fields relevant to selected video.
- Move all python dependencies into setup.py to simplify XBlock installation.

### Fixed

- Various bugs.

## [0.4.0] - 2017-02-07

### Added

- Vimeo backend support
- Brightcove content protection and auto-quality
  - On API authentication uploads two custom Ingest Profiles:
    - Creates new API credentials with required permissions
    - HLS for auto quality
    - HLSe for auto qualify & encryption

- Add new UI controls after a user has authenticated against Brightcove API:
  - View video tech info.
  - Send video re-transcode request on a Brightcove side.

- Default transcripts upload:
  - Allows to fetch transcripts from the platform and store them into XBlock.
  - Supports: Brightcove, Youtube & Wistia.
  - Brightcove & Wistia require API authentication before default transcripts
  upload can work.

- Dev process improvements:
  - Code Climate integration to track code quality.
  - Coveralls.io integration to track test coverage.

### Changed

- Now TravisCI runs eslint and python unit tests on every commit.

### Fixed

- Various bugfixes and improvements.

## [0.3.0-alpha] - 2017-01-16

### Added

- SRT subtitles support.
- Transcripts downloading for students.
- TravisCI integration: pylint to begin with.

## Fixed

- Code cleanup.
- Various bugs.

## [0.2.0-alpha] - 2017-01-04

### Added

- Interactive transcripts.
- Closed captions.
- Open edX Analytic events.
- Brightcove playerID support.
- Handouts upload/download.
- Context menu.
- Offset start/end time.
- A11y: keyboard-only access, screen readers support.

## [0.1.0-alpha] - 2016-11-30

### Added

- Youtube support.
- Wistia support.
- Basic Brightcove support.
- Different playback rates support.
- Video player state load/save.
- All video players share skin similar to Open edX's video module.

[0.1.0-alpha]: https://github.com/raccoongang/xblock-video/tree/v0.1.0-alpha
[0.2.0-alpha]: https://github.com/raccoongang/xblock-video/compare/v0.1.0-alpha...v0.2.0-aplha
[0.3.0-alpha]: https://github.com/raccoongang/xblock-video/compare/v0.2.0-alpha...v0.3.0-aplha
[0.4.0]: https://github.com/raccoongang/xblock-video/compare/v0.3.0-alpha...v0.4.0
[0.5.0]: https://github.com/raccoongang/xblock-video/compare/v0.4.0...v0.5.0
[0.6.0]: https://github.com/raccoongang/xblock-video/compare/v0.5.0...v0.6.0
[0.6.1]: https://github.com/raccoongang/xblock-video/compare/v0.6.0...v0.6.1
[0.6.2]: https://github.com/raccoongang/xblock-video/compare/v0.6.1...v0.6.2
[0.6.3]: https://github.com/raccoongang/xblock-video/compare/v0.6.2...v0.6.3
[0.6.4]: https://github.com/raccoongang/xblock-video/compare/v0.6.3...v0.6.4
[0.6.5]: https://github.com/raccoongang/xblock-video/compare/v0.6.4...v0.6.5
[0.6.6]: https://github.com/raccoongang/xblock-video/compare/v0.6.5...v0.6.6
[0.7.0]: https://github.com/raccoongang/xblock-video/compare/v0.6.6...v0.7.0
[0.7.1]: https://github.com/raccoongang/xblock-video/compare/v0.7.0...v0.7.1
[0.8.0]: https://github.com/raccoongang/xblock-video/compare/v0.7.1...v0.8.0
[0.9.0]: https://github.com/raccoongang/xblock-video/compare/v0.8.0...v0.9.0
[0.9.1]: https://github.com/raccoongang/xblock-video/compare/v0.9.0...v0.9.1
[0.9.2]: https://github.com/raccoongang/xblock-video/compare/v0.9.1...v0.9.2
[0.9.3]: https://github.com/raccoongang/xblock-video/compare/v0.9.2...v0.9.3
[0.9.4]: https://github.com/raccoongang/xblock-video/compare/v0.9.3...v0.9.4
[0.10.0]: https://github.com/raccoongang/xblock-video/compare/v0.9.4...v0.10.0
[0.10.1]: https://github.com/raccoongang/xblock-video/compare/v0.10.0...v0.10.1
[Unreleased]: https://github.com/raccoongang/xblock-video/compare/v0.10.1...HEAD
