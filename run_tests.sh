#!/usr/bin/env bash
set -eux

while test $# -gt 0
do
    case "$1" in
        --with-coverage) WITH_COVERAGE=1
            ;;
        *) echo "Ignoring argument $1"
            ;;
    esac
    shift
done

if [ ! -z ${WITH_COVERAGE+x} ]; then
    COVER_APP_CMD_PREFIX="coverage run --source=apps,make_a_plea"
    COVER_API_CMD_PREFIX="coverage run -a --source=api"
    echo Running tests WITH coverage
else
    COVER_APP_CMD_PREFIX=
    COVER_API_CMD_PREFIX=
    echo Running tests WITHOUT coverage
fi

DJANGO_SETTINGS_MODULE=make_a_plea.settings.testing
export DJANGO_SETTINGS_MODULE

pip install -Ur requirements/testing.txt 2>&1
python ./manage.py compilemessages 

coverage erase;
$COVER_APP_CMD_PREFIX ./manage.py test
RET1=$?
$COVER_API_CMD_PREFIX ./manage.py test --settings=api.settings.testing -p api_test_*.py
RET2=$?

if [ ! -z ${WITH_COVERAGE+x} ]; then
    coverage xml --omit=*/migrations/*
    coverage html --omit=*/migrations/*
fi

exit $((RET1 + RET2))
