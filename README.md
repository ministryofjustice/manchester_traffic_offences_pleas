Make a Plea
===========

A simple, user-friendly online service for citizens to submit pleas for summary motoring offences.

Dependencies
------------

- VirtualBox
- Vagrant
- Docker & Docker-compose

NOTE: Vagrant or docker can be used to set up a local dev environment

Installation
------------

Clone the repository:

    git clone git@github.com:ministryofjustice/manchester_traffic_offences_pleas.git

Running tests
-------------

To prepare to run the tests see the [Test Setup](#test-setup) section below

# API tests:

```shell
./run_api_tests.sh
```

# App unit tests:

```shell
./run_tests.sh
```

# BDD tests:

```shell
python manage.py behave
```

### To run a dev environment with vagrant:

Create your own local.py:

    cp manchester_traffic_offences/settings/local.py.example make_a_plea/settings/local.py

    vagrant up
    vagrant ssh

The vagrant bootstrap script will install everything you need to run the application server. All you need to do is override the relevant email settings in your local.py.

Once you're ssh'd in run:

    ./manage.py runserver 0.0.0.0:8000

to run the development web server, and browse to http://localhost:8000 to see the server.


### To run a dev environment using docker:

copy `docker/sample-local-env` to `docker/local-env`

run:

    docker-compose up

This will install dependencies from requirements.txt but initial migrations will need to be run manually - see below.

Navigate to:

    {ip of docker machine}:8000

To get an interactive prompt (needed to run migrations, etc.), run:

    docker-compose run django /bin/bash

You can also run commands directly, e.g:

    docker-compose run django ./manage.py migrate


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

Environment Variables
---------------------

Some environemnt variables override settings from the settings file. If you have specific needs you may set DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT.

Test Setup
----------

Before you can run all the tests locally you may need to follow these steps.

Make sure you have Python 2.7. 

Create a virtualenv.

Install postgres locally (alternatively see [Environment Variables](#environment-variables):

```shell
sudo apt install postgresql
```

Make sure that you have the equivalent of these lines high enough up your pgi\_hba.conf to take effect:

```pre
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
```

Note that these rules are overly broad and this readme welcomes changes with more specific rules.

Restart your postgres server to ensure all connections are using the new rules.

```shell
/etc/init.d/postgresql restart
```

Create a user capable of creating databases and installing database extensions:

```shell
postgres@localhost$ createuser -sdW <username as per make_a_plea/settings/testing.py>
Password: <password as per make_a_plea/settings/testing.py>
```

Configure AWS keys for testing SMTP via AWS-SMTP gateway:

```shell
# TODO
```
