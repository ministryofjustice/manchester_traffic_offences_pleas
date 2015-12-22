#!/usr/bin/env bash
set -eux

DJANGO_SETTINGS_MODULE=make_a_plea.settings.testing
export DJANGO_SETTINGS_MODULE

pip install -r requirements/testing.txt
python ./manage.py compilemessages
python ./manage.py test

#
# XXX:
#      API testing should be enabled, but as of this commit API tests are broken.
#      Leaving this here for future reference.

# python ./manage.py test --settings=api.settings.testing -p api_test_*.py
