# xblock-video

[![Build Status](https://img.shields.io/circleci/project/raccoongang/xblock-video/dev.svg)](https://circleci.com/gh/raccoongang/xblock-video/tree/dev)
[![Coverage Status](https://img.shields.io/codecov/c/github/raccoongang/xblock-video/dev.svg)](https://codecov.io/gh/raccoongang/xblock-video)
[![GitHub release](https://img.shields.io/github/release/raccoongang/xblock-video.svg)](https://github.com/raccoongang/xblock-video/releases)

The Video XBlock is for embedding videos hosted on different video platforms
into your Open edX courses.

Supported video platforms:

- Brightcove
- Html5
- Vimeo
- Wistia
- Youtube

The idea of crowd-funded universal video-xblock was proposed by @natea
(Appsembler) at the Open edX Conference 2016 at Stanford. It was well-received
and several companies offered to sponsor the initial development.

Appsembler initially contracted with Raccoon Gang to build the [wistia-xblock]
as a prototype ([see the Github repo]), and later created a new Video XBlock
featuring universal pluggable interface with several video hosting providers
support:

[wistia-xblock]: https://appsembler.com/blog/why-open-edx-needs-an-alternative-video-xblock/
[see the Github repo]: https://github.com/appsembler/xblock-wistia

Appsembler and Raccoon Gang will be co-presenting [a talk about the
video-xblock] at the Open edX Con 2017 in Madrid.

[a talk about the video-xblock]: https://openedx2017.sched.com/event/9zf6/lightning-talks

We welcome folks from the Open edX community to contribute additional video
backends as well as report and fix issues.

Thanks to [InterSystems] and [Open University] for sponsoring the initial
version of the Video XBlock!

[InterSystems]: https://www.intersystems.com
[Open University]: https://www.open.ac.uk

## Installation

```shell
sudo -sHu edxapp
source ~/edxapp_env
# Install VideoXBlock using pip
pip install --process-dependency-links -e "git+https://github.com/appsembler/xblock-video.git@dev#egg=video_xblock"
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

To embed a video simply copy & paste its URL into a `Video URL` field.

Sample supported video URLs:

- Brightcove: https://studio.brightcove.com/products/videocloud/media/videos/12345678 or https://studio.brightcove.com/products/videos/12345678
- HTML5: https://example.com/video.mpeg|mp4|ogg|webm
- Vimeo: https://vimeo.com/abcd1234
- Wistia: https://raccoongang.wistia.com/medias/xmpqebzsya
- Youtube: https://www.youtube.com/watch?v=3_yD_cEKoCk and others.

### Brightcove

To successfully use videos hosted on Brightcove Videocloud service one must
provide valid Brightcove `account_id` associated with the video. To find out
your `account_id` go to [Videocloud studio] -> _Admin_ -> _Account Information_.

[Videocloud studio]: https://studio.brightcove.com/products/videocloud/home

#### Connect to Brightcove Platform

1. Grab your [BC_TOKEN] from Brightcove Videocloud:
   1. Login to [Videocloud Studio] as you normally do.
   1. With any page in Studio open, open the developer tools for the browser,
      go to the Console, and paste in the following code:

       ```js
       var cookiesArray = document.cookie.split(";"), cookiesObj = {}, i, tmpArray = [];
       for (i = 0; i < cookiesArray.length; i++) {
           tmpArray = cookiesArray[i].split("=");
           if (tmpArray[0].indexOf('BC_TOKEN') > -1) {
               cookiesObj.BC_TOKEN = tmpArray[1];
           }
       }
       window.prompt("BC_TOKEN:", cookiesObj.BC_TOKEN);
       ```

      and press `<return>`.
   1. You should see a prompt appear that contains your BC_TOKEN.
    ![BC_TOKEN sample](https://learning-services-media.brightcove.com/doc-assets/video-cloud-apis/ingest-profiles-api/guides/prompt-with-token-safari.png "Sample BC_TOKEN")
1. Open Video XBlock settings, Advanced tab. Scroll down to `Video API Token` section.
1. Put `BC_TOKEN` taken from Brightcvove into `Client Token` field.
1. Click on `Connect to video platform` button.

[Videocloud Studio]: https://studio.brightcove.com/products/videocloud/home
[BC_TOKEN]: https://docs.brightcove.com/en/video-cloud/media-management/guides/authentication.html

#### Enable content encryption and/or autoquality

Given you've connected XBlock to Brightcove platform and have a Video XBlock with a video from Brightcove. You can enablevideo content encryption and/or auto-quality.

To do so:
1. Go to Advanced settings tab.
1. Scroll down to `Brightcove content protection` section.
1. Select `Autoquality` or `Autoquality & Encryption`.
1. Click `Re-transcode this video` button.

Re-transcode is performed by Brightcove's Videocloud and takes few minutes. After it's done `Brightcove Video tech info` section will be updated.

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

VideoXBlock is bundled with a set of XBlock-SDK Workbench scenarios.
See [workbench docs](/video_xblock/workbench/README.md) for details.

## License

The code in this repository is licensed under the GPL v3 licence unless
otherwise noted.

Please see `LICENSE` file for details.
