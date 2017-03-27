# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

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
[Unreleased]: https://github.com/raccoongang/xblock-video/compare/v0.6.2...HEAD
