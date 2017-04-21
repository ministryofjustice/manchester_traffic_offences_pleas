FROM python:2.7

COPY /docker/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

RUN chown root:root /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem && \
    chmod 600 /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem

ENV APP_HOME=/makeaplea/
ENV DJANGO_SETTINGS_MODULE=make_a_plea.settings.docker
WORKDIR $APP_HOME

ADD apt/ $APP_HOME/apt

RUN apt-get -y update && $APT_HOME/apt/production.sh

COPY requirements.txt $APP_HOME
ADD requirements/ $APP_HOME/requirements/

RUN pip install -r requirements.txt

RUN mkdir /user_data
RUN mkdir /user_data/.gnupg
RUN mkdir -p make_a_plea/assets

VOLUME ["/user_data"]

COPY . $APP_HOME

RUN gpg --import /makeaplea/docker/user_data.gpg

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages

CMD ["./run.sh"]

EXPOSE 9080

