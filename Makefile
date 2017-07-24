REPO=thraxil
APP=countryx

JS_FILES = media/js/game.js media/js/faculty.js media/js/sim_allpaths.js

include *.mk

jenkins: $(SENTINAL) check jshint jscs flake8 test

all: flake8 test eslint
