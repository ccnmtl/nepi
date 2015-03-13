import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/nepi/nepi/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/nepi/nepi/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'nepi.settings_production'

import django.core.handlers.wsgi
import django
django.setup()

application = django.core.handlers.wsgi.WSGIHandler()
