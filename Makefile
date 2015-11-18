MANAGE=./manage.py
APP=nepi
FLAKE8=./ve/bin/flake8

jenkins: ./ve/bin/python check test flake8 jshint jscs

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

test: ./ve/bin/python
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=10

runserver: ./ve/bin/python check
	$(MANAGE) runserver

migrate: ./ve/bin/python check jenkins
	$(MANAGE) migrate

check: ./ve/bin/python
	$(MANAGE) check

shell: ./ve/bin/python
	$(MANAGE) shell_plus

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint --config=.jshintrc media/js/captcha.js media/js/dashboard.js media/js/people.js media/js/profile.js media/js/util.js

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs  media/js/captcha.js media/js/dashboard.js media/js/people.js media/js/profile.js media/js/util.js

node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

node_modules/jscs/bin/jscs:
	npm install jscs --prefix .

clean:
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm celerybeat-schedule
	rm .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make check
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make check
	make test
	make migrate
	make flake8

makemessages: ./ve/bin/python
	$(MANAGE) makemessages -l en --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html"
	$(MANAGE) makemessages -l fr --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html"
	$(MANAGE) makemessages -l pt --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html"

compilemessages: ./ve/bin/python
	$(MANAGE) compilemessages


# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python check jenkins
	createdb $(APP)
	$(MANAGE) syncdb --noinput
	make migrate
