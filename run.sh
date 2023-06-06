#!/bin/bash

case ${DOCKER_STATE} in
migrate)
    echo "running migrate"
    ./manage.py migrate
    ;;
esac

gunicorn make_a_plea.wsgi --bind=0.0.0.0:3000
service nginx start
