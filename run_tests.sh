#!/usr/bin/env bash
set -eux

DJANGO_SETTINGS_MODULE=make_a_plea.settings.testing
export DJANGO_SETTINGS_MODULE

# TODO: move this to a manage.py task to speed up regular test running 
pip install -r requirements/testing.txt

python ./manage.py compilemessages

# Unit tests
python ./manage.py test 

# API tests
python ./manage.py test --settings=api.settings.testing -p api_test_*.py

# BDD tests for individual djago apps
coverage run --source='.' manage.py test plea --behave_verbose --settings=make_a_plea.settings.bdd --behave_browser firefox

# Integration tests, top-level 
coverage run --source='.' -m behave --junit --junit-directory features/behave-reports features/

# Enable these when we have a better understanding of how they may affect current coverage reports on Jenkins
#coverage combine .coverage
#coverage html

