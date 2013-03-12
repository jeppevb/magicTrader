import os
import sys

sys.path.append('/srv/www/magictrader.kyomu.dk')

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/magictrader.kyomu.dk/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()