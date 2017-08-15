FROM python:2.7

ENV DJANGO_SETTINGS_MODULE=make_a_plea.settings.docker
WORKDIR /makeaplea

# Debian dependencies
COPY apt/ ./apt
RUN apt-get -y update && ./apt/production.sh

# Python dependencies
COPY requirements.txt ./requirements.txt
COPY requirements/ ./requirements
RUN pip install -r requirements.txt

RUN mkdir -p /user_data/.gnupg ./make_a_plea/assets

VOLUME ["/user_data"]

COPY . .

RUN gpg --import /makeaplea/docker/sustainingteamsupport-public-key.gpg

RUN python manage.py collectstatic --noinput \
  && python manage.py compilemessages

CMD ["./run.sh"]

EXPOSE 9080

