.PHONY=all,quality,test

all: quality test

clean:
	-rm -rf node_modules/

test: test-py

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

quality: quality-py quality-js

quality-py:
	-pep8 . --format=pylint --max-line-length=120
	-pylint -f colorized video_xblock

quality-js:
	eslint video_xblock/static/js/

deps:
	pip install -r requirements.txt
	bower install

deps-test:
	pip install -r test_requirements.txt

tools:
	npm install "eslint@^2.12.0" eslint-config-edx "eslint-plugin-dollar-sign@0.0.5" "eslint-plugin-import@^1.9.2"

package:
	echo "Here be static dependencies packaging"
