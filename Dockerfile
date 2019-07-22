FROM python:2.7

ENV APP_HOME=/makeaplea/
ENV DJANGO_SETTINGS_MODULE=make_a_plea.settings.docker
WORKDIR $APP_HOME

# Debian dependencies
COPY apt/ $APP_HOME/apt
RUN apt-get -y update && $APP_HOME/apt/production.sh

# Python dependencies
COPY requirements.txt $APP_HOME
COPY requirements/ $APP_HOME/requirements/
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary 

RUN mkdir /user_data
RUN mkdir /user_data/.gnupg
RUN mkdir -p make_a_plea/assets

VOLUME ["/user_data"]

COPY . $APP_HOME

RUN gpg --import /makeaplea/docker/sustainingteamsupport-public-key.gpg

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages

CMD ["./run.sh"]

EXPOSE 9080

