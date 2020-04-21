"""Setup for video XBlock."""

import os
import re
from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)

    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def package_data(pkg, roots):
    """
    Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


VERSION = get_version('video_xblock', '__init__.py')
DESCRIPTION = 'Video XBlock to embed videos hosted on different video platforms into your courseware'


setup(
    name='video-xblock',
    version=VERSION,
    description=DESCRIPTION,
    license='GPL v3',
    packages=[
        'video_xblock',
    ],
    install_requires=[
        'XBlock>=0.4.10,<2.0.0',
        'xblock-utils',
        'le-pycaption',
        'requests>=2.9.1,<3.0.0',
        'babelfish>=0.5.5,<0.6.0',
    ],
    entry_points={
        'xblock.v1': [
            'video_xblock = video_xblock:VideoXBlock',
        ],
        'video_xblock.v1': [
            'youtube-player = video_xblock.backends.youtube:YoutubePlayer',
            'wistia-player = video_xblock.backends.wistia:WistiaPlayer',
            'brightcove-player = video_xblock.backends.brightcove:BrightcovePlayer',
            'dummy-player = video_xblock.backends.dummy:DummyPlayer',
            'vimeo-player = video_xblock.backends.vimeo:VimeoPlayer',
            'html5-player = video_xblock.backends.html5:Html5Player',
        ]
    },
    package_data=package_data("video_xblock", ["static", "backends", "public", "tests", "workbench"]),
)
