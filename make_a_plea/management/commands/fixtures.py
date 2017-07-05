"""
Fixtures
========

To simplify testing of time-dependant and related fields in the makeaplea app,
some fixtures must be dynamically generated. Others may be loaded directly.

This module constructs the fixtures command from separate mixin classes.

```
# Load a large number of fixtures to run performance tests
./manage.py fixtures --method load --category performance --count 100

# Verbosely generate Django fixtures for cucumber tests (load them later with ./manage.py loaddata)
./manage.py fixtures --method generate --category cucumber --verbose true

# Load core fixtures to be able to demo the app
./manage.py fixtures --method load --category core

# Which is the default and therefore the same as this
./manage.py fixtures

An alternative approach to dynamic fixtures could be:

 * mocking all calls to time
 * ensure no time bombs in libs we use (e.g. ssl cipher deprecation)
 * ensure time is mocked in phantomjs etc.

"""

from django.core.management.base import BaseCommand

from make_a_plea.management.commands.fixture_categories import FixtureCategories
from make_a_plea.management.commands.fixture_methods import FixtureMethods


class Command(BaseCommand, FixtureMethods, FixtureCategories):
    """A command that pulls together fixture definitions and fixture methods"""

    help = """Generate fixture files or load fixtures directly."""
    DEFAULT_CASE_COUNT = 10000
    BATCH_SIZE = 100  # Generate data in batches to avoid excessive memory use
    COURT_FRACTION = 1.5  # Approximately this fraction of courts vs cases

    def add_arguments(self, parser):
        parser.add_argument(
            '--method',
            action='store',
            choices=self.METHOD_ARGS,
            dest="method",
            default="load")
        parser.add_argument(
            '--category',
            action='store',
            choices=self.CATEGORY_ARGS,
            dest="category",
            default="core")
        parser.add_argument(
            '--count',
            action='store',
            type=int,
            dest="count",
            default=self.DEFAULT_CASE_COUNT)
        parser.add_argument(
            '--verbose',
            action='store',
            type=bool,
            dest="verbose",
            default=False)

    def handle(self, *args, **options):
        self.options = options
        self.init_category()
        self.init_method()
        self.method()
