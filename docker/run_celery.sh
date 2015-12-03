#!/usr/bin/env bash

export PATH=$PATH:/makeaplea/

cd /makeaplea && source /makeaplea/docker/celery_defaults && celery worker -A apps.plea.tasks:app

