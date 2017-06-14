#!/bin/bash
# Update dependencies and the database
pip install -r requirements/dev.txt && pip install -r requirements/testing.txt
./manage.py migrate
