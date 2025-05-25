import os
import sys

import django


def init_django():
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )
    sys.path.append(BASE_DIR)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
    django.setup()
