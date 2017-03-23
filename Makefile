SHELL := /bin/bash
.PHONY=all,quality,test

all: quality test

clean:
	-rm -rf node_modules/

test: test-py test-js

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

test-js:
	karma start video_xblock/static/video_xblock_karma.conf.js

quality: quality-py quality-js

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pylint -f colorized video_xblock
	pydocstyle -e

quality-js:
	eslint video_xblock/static/js/

dev-install:
	# Install package using pip to leverage pip's cache and shorten CI build time
	pip install --process-dependency-links -e .

deps-test:
	pip install -r test_requirements.txt
	bower install

tools:
	npm install

coverage:
	bash <(curl -s https://codecov.io/bash)

package:
	echo "Here be static dependencies packaging"
