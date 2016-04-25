from config.base import *  # flake8: noqa

try:
    from config.local import *  # flake8: noqa
except ImportError:
    print('Local settings file not found.')

