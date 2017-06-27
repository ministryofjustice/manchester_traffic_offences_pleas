#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/

export C_FORCE_ROOT=true

cd /makeaplea && source /makeaplea/docker/celery_defaults && celery worker -A apps.plea.tasks:app

