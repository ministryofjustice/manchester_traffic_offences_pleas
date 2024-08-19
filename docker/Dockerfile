FROM python:3.6

ARG ENV
ARG DJANGO_SETTINGS
ARG AWS_STORAGE_BUCKET_NAME

ENV APP_HOME=/makeaplea/
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS}.${ENV}
ENV AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}

RUN echo "${DJANGO_SETTINGS_MODULE}"

WORKDIR $APP_HOME

# Debian dependencies
COPY apt/ $APP_HOME/apt
RUN apt-get -y update && $APP_HOME/apt/production.sh
RUN apt-get -y install wkhtmltopdf

# Python dependencies
COPY requirements.txt $APP_HOME
COPY requirements/ $APP_HOME/requirements/
RUN pip install -r requirements.txt

RUN mkdir /user_data
RUN mkdir /user_data/.gnupg
RUN mkdir -p make_a_plea/assets

VOLUME ["/user_data"]

ARG uid=1000
ARG gid=51

RUN addgroup --gid $gid mygroup \
 && adduser --disabled-password --gecos "" --no-create-home --uid $uid --gid $gid myuser

COPY . $APP_HOME
RUN chown -R myuser:mygroup $APP_HOME

RUN gpg --import /makeaplea/docker/sustainingteamsupport-public-key.gpg

# Create the vagrant directories
RUN mkdir -p /home/vagrant
RUN mkdir -p /home/vagrant/.gnupg/

# Copy the run_celery.sh script and make it executable
COPY docker/run_celery.sh /makeaplea/docker/run_celery.sh
RUN chmod +x /makeaplea/docker/run_celery.sh

# Don't run as root user
USER 1000
CMD ["/makeaplea/docker/run_celery.sh"]

EXPOSE 3001