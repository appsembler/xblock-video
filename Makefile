PATH := node_modules/.bin:$(PATH)
SHELL := /bin/bash
SELENIUM_BROWSER ?= chrome

.PHONY=all,quality,test

bower_dir := bower_components
vendor_dir := video_xblock/static/vendor
vendored_js := video.js/dist/video.min.js\
			 videojs-contextmenu-ui/dist/videojs-contextmenu-ui.min.js\
			 videojs-contextmenu/dist/videojs-contextmenu.min.js\
			 videojs-offset/dist/videojs-offset.min.js\
			 videojs-transcript/dist/videojs-transcript.min.js\
			 videojs-vimeo/src/Vimeo.js\
			 videojs-wistia/vjs.wistia.js\
			 videojs-youtube/dist/Youtube.min.js

vendored_css := video.js/dist/video-js.min.css
vendored_fonts := video-js/dist/font/VideoJS.eot

all: quality test

clean: # Clean working directory
	-rm -rf node_modules/
	-rm -rf bower_components/
	-rm -rf dist/
	-find . -name *.pyc -delete
	-rm *acceptance*.png *acceptance*.log

test: test-py test-js test-acceptance ## Run unit and acceptance tests

test-py: ## Run Python tests
	nosetests video_xblock.tests.unit --with-coverage --cover-package=video_xblock

test-js: ## Run JavaScript tests
	karma start video_xblock/static/video-xblock-karma.conf.js

test-acceptance:
	SELENIUM_BROWSER=$(SELENIUM_BROWSER) \
	python run_tests.py video_xblock/tests/acceptance \
	--with-coverage --cover-package=video_xblock

quality: quality-py quality-js ## Run code quality checks

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pydocstyle
	pylint -f colorized video_xblock

quality-js:
	eslint video_xblock/static/js/

dev-install:
	# Install package using pip to leverage pip's cache and shorten CI build time
	pip install --process-dependency-links -e .

deps-test: ## Install dependencies required to run tests
	pip install -Ur test_requirements.txt
	pip install -r $(VIRTUAL_ENV)/src/xblock-sdk/requirements/base.txt

deps-js: tools
	bower install

tools: ## Install development tools
	npm install

coverage-unit: ## Send unit tests coverage reports to coverage sevice
	bash <(curl -s https://codecov.io/bash) -cF unit

coverage-acceptance: ## Send acceptance tests coverage reports to coverage sevice
	bash <(curl -s https://codecov.io/bash) -cF acceptance

clear-vendored:
	rm -rf $(vendor_dir)/js/*
	rm -rf $(vendor_dir)/css/*
	mkdir $(vendor_dir)/css/font

$(vendored_js): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/js/$(@F)

$(vendored_css): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/css/$(@F)

$(vendored_fonts): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/css/font/$(@F)

vendored: $(vendored_js) $(vendored_css) $(vendored_fonts)  ## Update vendored JS/CSS assets
	@echo "Packaging vendor files..."

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
