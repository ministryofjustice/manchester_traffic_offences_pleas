#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/
export C_FORCE_ROOT=true

# Source the Celery defaults
# source /makeaplea/docker/celery_defaults

# Start the Celery worker
# celery --app=make_a_plea.celery:app worker --loglevel DEBUG --queues pet-development-celery

cd /makeaplea && source /makeaplea/docker/celery_defaults && celery -A make_a_plea.celeryapp worker --loglevel=info --queues pet-development-celery

# supervisord -c /makeaplea/docker/supervisord.conf

# while true
# do
#   sleep 60
# done
