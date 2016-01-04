#!/usr/bin/env bash
set -eux

DJANGO_SETTINGS_MODULE=make_a_plea.settings.testing
export DJANGO_SETTINGS_MODULE

pip install -r requirements/testing.txt
python ./manage.py compilemessages
python ./manage.py test
python ./manage.py test --settings=api.settings.testing -p api_test_*.py
