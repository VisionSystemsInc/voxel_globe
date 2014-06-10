import os
import sys

apache_dir = os.path.dirname(__file__)
project = os.path.dirname(apache_dir)
workspace = os.path.dirname(project)
if workspace not in sys.path:
    sys.path.append(workspace)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nga.settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
