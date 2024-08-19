#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/

export C_FORCE_ROOT=true

cd /makeaplea && source /makeaplea/docker/celery_defaults && celery --app=make_a_plea.celery:app worker --loglevel DEBUG --queues pet-development-celery &
