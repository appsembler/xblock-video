[![Build Status](https://travis-ci.org/raccoongang/xblock-video.svg?branch=dev)](https://travis-ci.org/raccoongang/xblock-video)
[![Coverage Status](https://coveralls.io/repos/github/raccoongang/xblock-video/badge.svg?branch=dev)](https://coveralls.io/github/raccoongang/xblock-video?branch=dev)

# xblock-video
XBlock to embed videos hosted on different video platform into your courses.

## Installation

```bash
sudo -sHu edxapp
source ~/edxapp_env
# Clone and install xblock
git clone https://github.com/raccoongang/xblock-video.git
cd xblock-video
pip install -e .
# Install external JavaScript dependencies
cd video_xblock/static
bower install
```

## Enabling in Studio
You can enable the Wistia xblock in studio through the advanced
settings:

1. From the main page of a specific course, click on *Settings*,
   *Advanced Settings* in the top menu.
1. Check for the *Advanced Module List* policy key, and add
   `"video_xblock"` in the policy value list.
   ![Advanced Module List](doc/img/advanced_settings.png)

1. Click on the *Save changes* button.

## Usage

TODO

## License

The code in this repository is licensed under the GPL v3 licence unless otherwise noted.

Please see `LICENSE` file for details.


## Tests

Assuming revealjs is installed as above, you can run python tests like so:

```nosetests video_xblock```

To get statement coverage:

```nosetests video_xblock --with-coverage --coverage-package=video_xblock```


