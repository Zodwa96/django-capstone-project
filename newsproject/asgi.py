"""ASGI config for newsproject, used by async-capable servers."""
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
application = get_asgi_application()
