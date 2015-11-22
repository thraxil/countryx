ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
MANAGE=./manage.py
APP=countryx
FLAKE8=./ve/bin/flake8

ifeq ($(TAG), undefined)
	IMAGE = thraxil/$(APP)
else
	IMAGE = thraxil/$(APP):$(TAG)
endif

jenkins: ./ve/bin/python validate jshint jscs flake8 test

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

test: ./ve/bin/python
	$(MANAGE) test

coverage: ./ve/bin/python flake8
	. ./ve/bin/activate && ./ve/bin/coverage run --source='countryx' ./manage.py test \
	&& ./ve/bin/coverage html -d reports --omit='*migrations*,*settings_*,*wsgi*'

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint media/js/game.js media/js/faculty.js media/js/sim_allpaths.js

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs media/js/game.js media/js/faculty.js media/js/sim_allpaths.js

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=9

runserver: ./ve/bin/python validate
	$(MANAGE) runserver

migrate: ./ve/bin/python validate jenkins
	$(MANAGE) migrate

validate: ./ve/bin/python
	$(MANAGE) validate

shell: ./ve/bin/python
	$(MANAGE) shell_plus

docker-pg:
	docker run --name cx-pg \
	-e POSTGRES_PASSWORD=nothing \
	-e POSTGRES_USER=postgres \
	-d \
	postgres

docker-test: build
	docker run -it -p 31000:8000 \
	--link cx-pg:postgresql \
	-e DB_NAME=postgres \
	-e SECRET_KEY=notreal \
	-e DB_PASSWORD=nothing \
	-e DB_USER=postgres \
	thraxil/countryx

node_modules/jshint/bin/jshint:
	npm install jshint

node_modules/jscs/bin/jscs:
	npm install jscs

clean:
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm celerybeat-schedule
	rm .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make validate
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make validate
	make test
	make migrate
	make flake8

# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python validate jenkins
	createdb $(APP)
	$(MANAGE) syncdb --noinput
	make migrate

wheelhouse/requirements.txt: requirements.txt
	mkdir -p wheelhouse
	docker run --rm \
	-v $(ROOT_DIR):/app \
	-v $(ROOT_DIR)/wheelhouse:/wheelhouse \
	ccnmtl/django.build
	cp requirements.txt wheelhouse/requirements.txt
	touch wheelhouse/requirements.txt

build: wheelhouse/requirements.txt
	docker build -t $(IMAGE) .
