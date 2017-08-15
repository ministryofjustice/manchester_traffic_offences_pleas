# Make a Plea

A simple, user-friendly online service for citizens to submit pleas for summary motoring offences.

## Dependencies
- [docker-compose](https://docs.docker.com/compose/) for local development and testing

## Usage

#### `make dev-makeaplea`
Run the makeaplea frontend app. Also just `make dev`

If you need to run the app on a port other than `8000` you can set the exposed
port with the `PORT` environment variable.

`PORT=8002 make dev`

#### `make dev-api`
Run the makeaplea api app

The `PORT` environment variable can be used to override the default port of `8001`

#### `make dev-psql`
Open a psql client against the dev database.

#### `make dev-exec`
Get a docker exec prefix to run arbitrary commands against the dev makeaplea container.

For example:

#### `$(make dev-exec) python manage.py createsuperuser`
Create a Django superuser.

#### `$(make dev-exec) bash`
Open a bash shell

#### `make stop`
Stop all dev and test containers

### `make rm`
Remove all dev and test containers

## Front-end development
Front-end development uses the [gulp](http://gulpjs.com/) task runner.
These should be run against the dev container with `$(make dev-exec) gulp ...`

### Gulp tasks

#### `gulp clean`

Completely removes the `/make_a_plea/assets` directory.

#### `gulp healthcheck`

Creates `/make_a_plea/assets/healthcheck.txt` used for uptime stats.

#### `gulp sass`

Compiles all SASS source files to CSS stylesheets and sourcemaps into the `/make_a_plea/assets/stylesheets` and 
`/make_a_plea/assets/maps` directories.

#### `gulp js`

Compiles all JavaScript modules and scripts to the `/make_a_plea/assets/javascripts` directories and copies over
the vendor dependencies.

#### `gulp lint`

Runs JSLint on all non-dependencies source JavaScript files.

#### `gulp test`

Runs the JavaScript modules tests. Configuration in `karma.conf.js`.

#### `gulp images`

Optimises all image assets into `/make_a_plea/assets/images`.

#### `gulp watch`

Sets up a watch on a number of directories. When a file has been changed, the relevant tasks are then automatically
run:
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


## Translations

Translations for the Welsh language are currently achieved using gettext and .po language files.

When content requiring translation has been added, the
[source English language .po file](https://github.com/ministryofjustice/manchester_traffic_offences_pleas/blob/master/conf/locale/en/LC_MESSAGES/django.po)
should be updated. To do so, run the makemessages script, which will update the .po file to include the latest
source strings:

```
./makemessages.sh
```

It may then be necessary to manually find strings marked as fuzzy, and check the source string matches the
translation string in all cases.

Once the file has been updated, it needs to be submitted to the relevant translation team, who should then provide
an updated Welsh language .po file. Replace the existing
`/conf/locale/cy/LC_MESSAGES/django.po` with this file, then compile the messages:

```
./manage.py compilemessages
```

## Testing

#### `make test`
Run all tests

#### `make test-unit`
Run the unit tests

#### `make test-cucumber`
Run the cucumber tests

#### `make test-psql`
Open a psql client against the test database
