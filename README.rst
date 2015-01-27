Make a Plea
###########

A simple, user-friendly online service for citizens to submit pleas for summary motoring offences.

Dependencies
------------

-  `Virtualenv <http://www.virtualenv.org/en/latest/>`__
-  `Python 2.7 <http://www.python.org/>`__ (Can be installed using ``brew``)
-  `Postgres 9.3+ <http://www.postgresql.org/>`__
-  NPM - brew install npm; npm install

Installation
------------

Clone the repository:

::

    git clone git@github.com:ministryofjustice/manchester_traffic_offences_pleas.git

Next, create the environment and start it up:

::

    cd manchester_traffic_offences_pleas
    virtualenv env --prompt=\(mtop\)
    source env/bin/activate

Install python dependencies:

::

    pip install -r requirements/local.txt

Create the database inside postgres. Type ``psql`` to enter postgres,
then enter:

::

    CREATE DATABASE manchester_traffic_offences WITH ENCODING 'UTF-8';

For OSX, update the ``PATH`` and ``DYLD_LIBRARY_PATH`` environment
variables if necessary:

::

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/MacOS/lib/:$DYLD_LIBRARY_PATH"

Create a ``local.py`` settings file from the example file:

::

    cp manchester_traffic_offences_pleas/settings/.example.local.py manchester_traffic_offences_pleas/settings/local.py

Sync and migrate the database: When prompted to create an Admin user,
accept all defaults and use password 'admin'.

::

    ./manage.py syncdb
    ./manage.py migrate
    ./manage.py test

Start the server:

::

    ./manage.py runserver 8000

Dev
---

Each time you start a new terminal instance you will need to run the
following commands to get the server running again:

::

    source env/bin/activate

    ./manage.py runserver 8000

Troubleshooting
---------------

If you are experiencing errors when creating and syncing the database,
make sure the following are added to your ``PATH`` var (amend path to
postgres as necessary):

::

    export PATH="/Applications/Postgres.app/Contents/Versions/9.3/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/Versions/9.3/lib/:$DYLD_LIBRARY_PATH"

Notes
-----

The content in manchester_traffic_offences/assets-src/stylesheets/elements/ is from https://github.com/alphagov/govuk_elements/tree/master/public/sass/elements and should be updated regularly.
