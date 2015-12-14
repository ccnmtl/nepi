APP=nepi
JS_FILES=media/js/captcha.js media/js/dashboard.js media/js/people.js media/js/profile.js media/js/util.js

all: jenkins

include *.mk

makemessages: check
	$(MANAGE) makemessages -l en --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html" --ignore="node_modules"
	$(MANAGE) makemessages -l fr --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html" --ignore="node_modules"
	$(MANAGE) makemessages -l pt --ignore="ve" --ignore="login.html" --ignore="password*.html" --ignore="registration*.html" --ignore="node_modules"

compilemessages: check
	$(MANAGE) compilemessages
