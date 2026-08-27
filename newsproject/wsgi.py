"""WSGI config for newsproject, used by gunicorn and other WSGI servers."""
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
application = get_wsgi_application()
