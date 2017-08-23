#!/bin/bash
set -e

echo "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST/$POSTGRES_DB"
until psql postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST/$POSTGRES_DB -c '\l' >/dev/null 2>&1; do
  >&2 echo "Waiting for Postgres"
  sleep 1
done
>&2 echo "Postgres up on postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST/$POSTGRES_DB"

python manage.py migrate
python manage.py loaddata docker/courts.json docker/user.json
python manage.py runserver 0.0.0.0:8000
