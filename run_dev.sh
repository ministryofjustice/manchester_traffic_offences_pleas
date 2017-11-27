#!/usr/bin/env bash

service rabbitmq-server start
service postgresql start

mailmock -p 1025 -o /tmp/mailmock -n &
celery worker -A make_a_plea -D
sleep 2
python ./manage.py runserver 0.0.0.0:80
