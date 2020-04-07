Make a Plea
===========

A simple, user-friendly online service for citizens to submit pleas for summary motoring offences.

Installation
------------

Clone the repository:

    git clone git@github.com:ministryofjustice/manchester_traffic_offences_pleas.git


### To run a dev environment locally:

You'll need:
 - python 3.6
 - postgres database with hstore
 - rabbit-mq for celery tasks

`apt/development.sh` should have all the dependencies you need. Python packages are in `requirements/`. You can set up virtualenv and do pip install.

Few steps you may also need:

    cp manchester_traffic_offences/settings/local.py.example make_a_plea/settings/local.py
    psql -c 'CREATE DATABASE manchester_traffic_offences;' -U postgres
    ./manage.py migrate --noinput
    ./manage.py compilemessages

Start server with:

    ./manage.py runserver

Start celery workers (if you need to test sending emails) with:

    celery worker -A make_a_plea


### To run a dev environment using docker:

There's a dev container that can be used to quickly spin up a working site, useful to run tests against without having to go through a local setup.

    docker build -t makeaplea:dev -f Dockerfile.dev .
    docker run makeaplea:dev


### Run Browser tests

To run locally, you will need Python behaving package installed with Selenium and Chrome/driver working.

Run on default host (127.0.0.1:8000)

	behave

Run in headless mode against another host (like docker). Omit @local as the mailmock needs local file access.

	behave -Dheadless -Dbase_url=http://172.17.0.2 -tags=-local


Front-end development
---------------------

Front-end development uses the [gulp](http://gulpjs.com/) task runner.

### Install dependencies

Make sure you have nodejs installed, then run:

    npm install

### Gulp tasks

#### `gulp clean`

Completely removes the `/make_a_plea/assets` directory.

#### `gulp healthcheck`

Creates `/make_a_plea/assets/healthcheck.txt` used for uptime stats.

#### `gulp sass`

Compiles all SASS source files to CSS stylesheets and sourcemaps into the `/make_a_plea/assets/stylesheets` and `/make_a_plea/assets/maps` directories.

#### `gulp js`

Compiles all JavaScript modules and scripts to the `/make_a_plea/assets/javascripts` directories and copies over the vendor dependencies.

#### `gulp lint`

Runs JSLint on all non-dependencies source JavaScript files.

#### `gulp test`

Runs the JavaScript modules tests. Configuration in `karma.conf.js`.

#### `gulp images`

Optimises all image assets into `/make_a_plea/assets/images`.

#### `gulp watch`

Sets up a watch on a number of directories. When a file has been changed, the relevant tasks are then automatically run:
- For files in `/make_a_plea/assets-src/stylesheets`: `sass` task
- For files in `/make_a_plea/assets-src/javascripts`: `lint`, then `js` tasks
- For files in `/make_a_plea/assets-src/images`: `images` task

#### `gulp build`

This is the default task, which can be run by simply using `gulp`. It runs the following tasks:
- `clean`
- `healthcheck`
- `lint`
- `js`
- `images`
- `sass`



Translations
------------

Translations for the Welsh language are currently achieved using gettext and .po language files.

When content requiring translation has been added, the [source English language .po file](https://github.com/ministryofjustice/manchester_traffic_offences_pleas/blob/master/conf/locale/en/LC_MESSAGES/django.po) should be updated. To do so, run the makemessages script, which will update the .po file to include the latest source strings:

    ./makemessages.sh

It may then be necessary to manually find strings marked as fuzzy, and check the source string matches the translation string in all cases.

Once the file has been updated, it needs to be submitted to the relevant translation team, who should then provide an updated Welsh language .po file. Replace the existing `/conf/locale/cy/LC_MESSAGES/django.po` with this file, then compile the messages:

    ./manage.py compilemessages
