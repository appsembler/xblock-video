.PHONY=all,quality,test

all: quality test

clean:
	-rm -rf node_modules/

test: test-py test-js

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

test-js:
	export DISPLAY=:99.0
	sh -e /etc/init.d/xvfb start
	karma start video_xblock/static/video_xblock_karma.conf.js
	sh -e /etc/init.d/xvfb stop

quality: quality-py quality-js

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pylint -f colorized video_xblock
	pydocstyle -e

quality-js:
	eslint video_xblock/static/js/

deps:
	pip install --process-dependency-links -r requirements.txt

deps-test:
	pip install -r test_requirements.txt
	bower install

tools:
	npm install bower "eslint@^2.12.0" "eslint-config-edx-es5@2.0.0" "eslint-plugin-dollar-sign@0.0.5" "eslint-plugin-import@^1.9.2"

coveralls:
	coveralls-lcov -v -n video_xblock/static/coverage/PhantomJS\ 2.1.1\ \(Linux\ 0.0.0\)/lcov.info > coverage.json
	coveralls --merge=coverage.json

prepare-for-js:
	npm install jasmine-core karma karma-jasmine karma-phantomjs-launcher karma-coverage karma-coveralls karma-chrome-launcher

package:
	echo "Here be static dependencies packaging"
