FROM python:2.7

COPY /docker/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

RUN chown root:root /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem && \
    chmod 600 /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

RUN groupadd makeaplea && useradd --create-home --home-dir /home/makeaplea -g makeaplea makeaplea

ENV APP_HOME=/makeaplea/
ENV DJANGO_SETTINGS_MODULE=make_a_plea.settings.docker
WORKDIR $APP_HOME

RUN apt-get -y update && apt-get -y install python-psycopg2

COPY requirements.txt $APP_HOME
ADD requirements/ $APP_HOME/requirements/

RUN pip install -r requirements.txt

USER makeaplea
COPY . $APP_HOME

CMD ["gunicorn",  "make_a_plea.wsgi", "--bind=0.0.0.0:9080"]

EXPOSE 9080
