JS_FILES ?= media/js

NODE_MODULES ?= ./node_modules
JS_SENTINAL ?= $(NODE_MODULES)/sentinal
JSHINT ?= $(NODE_MODULES)/jshint/bin/jshint
JSCS ?= $(NODE_MODULES)/jscs/bin/jscs
ESLINT ?= $(NODE_MODULES)/.bin/eslint

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install
	touch $(JS_SENTINAL)

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint $(JS_FILES)

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs $(JS_FILES)

node_modules/jshint/bin/jshint:
	npm install jshint

node_modules/jscs/bin/jscs:
	npm install jscs

eslint: $(JS_SENTINAL)
	$(ESLINT) $(JS_FILES)
