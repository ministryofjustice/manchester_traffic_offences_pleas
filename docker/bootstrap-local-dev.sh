#!/usr/bin/env bash 

cd /makeaplea/

python manage.py migrate
python manage.py loaddata docker/courts.json docker/user.json
