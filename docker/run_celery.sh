#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/
export C_FORCE_ROOT=true

# cd /makeaplea && source /makeaplea/docker/celery_defaults && celery -A make_a_plea.celeryapp worker --loglevel=info --queues pet-development-celery

while true
do
  sleep 60
done
