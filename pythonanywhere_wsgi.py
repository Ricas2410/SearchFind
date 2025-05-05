"""
WSGI config for PythonAnywhere deployment.

This file contains the WSGI application used by PythonAnywhere's web server.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/searchfind/SearchFind'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable to tell Django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'searchfind.settings'

# Set up Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
