FROM python:3.6

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

RUN mkdir /user_data
RUN mkdir /user_data/.gnupg
RUN mkdir -p make_a_plea/assets

VOLUME ["/user_data"]

COPY . $APP_HOME

RUN gpg --import /makeaplea/docker/sustainingteamsupport-public-key.gpg

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages

# bypass broken pipeline
ENV APP_BUILD_DATE="2020-06-17T09:26:53+0000"
ENV APP_GIT_COMMIT="master.a816014"
ENV APP_BUILD_TAG="a816014d47fe98db08f600476a7f811c3ac70f93"
ENV APP_VERSION="0.1.3-1731-ga816014"

CMD ["./run.sh"]

EXPOSE 9080

