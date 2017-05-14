# xblock-video

[![Build Status](https://img.shields.io/travis/raccoongang/xblock-video/dev.svg)](https://travis-ci.org/raccoongang/xblock-video)
[![Coverage Status](https://img.shields.io/codecov/c/github/raccoongang/xblock-video/dev.svg)](https://codecov.io/gh/raccoongang/xblock-video)
[![GitHub release](https://img.shields.io/github/release/raccoongang/xblock-video.svg)](https://github.com/raccoongang/xblock-video/releases)

The Video XBlock is for embedding videos hosted on different video platforms into your Open edX courses.

The idea of crowd-funded universal video-xblock was proposed by @natea (Appsembler) at the Open edX Conference 2016 at Stanford. It was well-received and several companies offered to sponsor the initial development.

Appsembler initially contracted with Raccoon Gang to build the [wistia-xblock](https://appsembler.com/blog/why-open-edx-needs-an-alternative-video-xblock/) as a prototype ([see the Github repo](https://github.com/appsembler/xblock-wistia)), and later created a new Video XBlock featuring universal pluggable interface with several video hosting providers support:

- Brightcove
- Html5
- Vimeo
- Wistia
- Youtube

Appsembler and Raccoon Gang will be co-presenting [a talk about the video-xblock](https://openedx2017.sched.com/event/9zf6/lightning-talks) at the Open edX Con 2017 in Madrid.

We welcome folks from the Open edX community to contribute additional video backends as well as report and fix issues.

Thanks to [InterSystems](http://www.intersystems.com) and [Open University](http://www.open.ac.uk) for sponsoring the initial version of the Video XBlock!

## Installation

```shell
sudo -sHu edxapp
source ~/edxapp_env
# Install VideoXBlock using pip
pip install --process-dependency-links -e "git+https://github.com/raccoongang/xblock-video.git@dev#egg=video_xblock"
```

## Enabling in Studio

You can enable the Video xblock in studio through the advanced
settings:

1. From the main page of a specific course, click on *Settings*,
   *Advanced Settings* in the top menu.
1. Check for the *Advanced Module List* policy key, and add
   `"video_xblock"` in the policy value list.
   ![Advanced Module List](doc/img/advanced_settings.png)

1. Click on the *Save changes* button.

## Usage

TODO

### Set default values in config files

Sample default settings in `/edx/app/edxapp/cms.env.json`:

```json
    "XBLOCK_SETTINGS": {
      "video_xblock": {
        "threeplaymedia_apikey": "987654321",
        "account_id": "1234567890"
      }
    }
```

## Development

Prereqs: [NodeJS >= 4.0](https://docs.npmjs.com/getting-started/installing-node#updating-npm)

Install development tools and dependencies:

```shell
> make tools deps-test
```

Run quality checks:

```shell
> make quality
```

Run tests:

```shell
> make test
```

## License

The code in this repository is licensed under the GPL v3 licence unless
otherwise noted.

Please see `LICENSE` file for details.
