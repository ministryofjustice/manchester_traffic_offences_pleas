FROM python:2.7

ENV APP_HOME=/makeaplea/
WORKDIR $APP_HOME

RUN apt-get -y update && apt-get -y install python-psycopg2

COPY /docker/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

RUN chown root:root /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem && \
    chmod 600 /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

COPY . $APP_HOME

RUN pip install -r requirements.txt

EXPOSE 8111

CMD ["gunicorn",  "make_a_plea.wsgi", "--bind=0.0.0.0:8111"]