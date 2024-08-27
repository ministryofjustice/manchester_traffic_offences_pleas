#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/
export C_FORCE_ROOT=true

# Run the migrations here?
# python manage.py migrate --noinput

cd /makeaplea && source /makeaplea/docker/celery_defaults && celery -A make_a_plea.celery worker --loglevel=info --queues pet-development-celery
