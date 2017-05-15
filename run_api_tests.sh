#!/usr/bin/env bash

pip install -r requirements/testing.txt
python ./manage.py test --settings=api.settings.base -p api_test_v0_*.py
