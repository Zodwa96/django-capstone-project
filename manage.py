#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Standard entry point used to run management commands such as
``runserver``, ``migrate``, ``test``, and the project's custom
``setup_permissions`` command.
"""
import os
import sys


def main():
    """Set the default settings module and hand off to Django's CLI."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django not installed") from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
