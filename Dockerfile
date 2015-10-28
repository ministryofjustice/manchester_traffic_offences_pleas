FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    python-pip \
    libpq-dev \
    postgresql-client-9.3\
    default-jre \
    git \
    python-dev \
    unoconv \
    gettext \
    libffi-dev \
    uwsgi

ENV APP_HOME /srv/pleaonline

WORKDIR $APP_HOME
ADD . $APP_HOME

RUN pip install -r requirements.txt

COPY /docker/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

RUN chown root:root /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem && \
    chmod 600 /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

ENV release_stage=dev

EXPOSE 8080

CD $APP_HOME

CMD ["python", "manage.py", "runserver"]

