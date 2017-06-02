"""
generate_fixtures
=================

To simplify testing of time-dependant fields in the makeaplea app, fixtures
must be dynamically generated.

An alternative approach could be:

 * mocking all calls to time
 * ensure no time bombs in libs we use (e.g. ssl cipher deprecation)
 * ensure time is mocked in phantomjs etc.

"""

import datetime
import os
import yaml
from subprocess import call

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import translation
from django.utils.translation import ugettext


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))


class Command(BaseCommand):

    help = """
This management command will produce various dynamic fixture files that can be
loaded to support BDD and other tests.
"""

    def handle(self, *args, **options):

        NOW = datetime.datetime.utcnow()
        ONE_DAY = datetime.timedelta(days=1)

        FIXTURES_SRC = [
            {
                # A Case ready for a user journey
                "model": "plea.case",
                "pk": 1,
                "fields": {
                    "urn": "00000000000",
                    "name": "Some Valid User",
                    "case_number": 123456,
                    "email": "root@localhost",
                    "email_permission": True,
                    "date_of_hearing": None,
                    "imported": True,
                    "ou_code": "B01CN02",
                    "initiation_type": "O",
                    "language": "en",
                    "sent": True,
                    "processed": False,
                    "created": NOW - 10 * ONE_DAY,
                    "completed_on": None,
                    "extra_data": """
                        {
                            "Surname": "Parker",
                            "Forename1": "Alice",
                            "Forename2": "Alice",
                            "DOB": "1950-01-29T22:21:21",
                            "Gender": "N",
                            "Address2": "Triumph Boulevard",
                            "PostCode": "H8 3X",
                            "Address1": "319 Harley St",
                            "DateOfHearing": "2017-03-29T20:18:28"
                        }
                    """.replace("\n", "").replace(" ", ""),
                },
            },

            # A Case that has already been completed
            {
                "model": "plea.case",
                "pk": 2,
                "fields": {
                    "urn": "00000000001",
                    "name": "Some Valid User Completed",
                    "case_number": 123457,
                    "email": "root@localhost",
                    "email_permission": True,
                    "date_of_hearing": None,
                    "imported": True,
                    "ou_code": "B01CN02",
                    "initiation_type": "O",
                    "language": "en",
                    "sent": True,
                    "processed": False,
                    "created": NOW - 10 * ONE_DAY,
                    "completed_on": NOW - 5 * ONE_DAY,
                    "extra_data": """
                        {
                            "Surname": "User Completed",
                            "Forename1": "Some",
                            "Forename2": "Valid",
                            "DOB": "1950-01-29T22:21:21",
                            "Gender": "N",
                            "Address2": "Triumph Boulevard",
                            "PostCode": "H8 3X",
                            "Address1": "77 Harley St",
                            "DateOfHearing": null
                        }
                    """.replace("\n", "").replace(" ", ""),
                },
            },

            # A Case that has already been completed and resulted
            {
                "model": "plea.case",
                "pk": 3,
                "fields": {
                    "urn": "00000000003",
                    "name": "Some Valid User Completed Resulted",
                    "case_number": 123458,
                    "email": "root@localhost",
                    "email_permission": True,
                    "date_of_hearing": NOW + 14 * ONE_DAY,
                    "imported": True,
                    "ou_code": "B01CN02",
                    "initiation_type": "O",
                    "language": "en",
                    "sent": True,
                    "processed": True,
                    "created": NOW - 10 * ONE_DAY,
                    "completed_on": NOW - 5 * ONE_DAY,
                    "extra_data": """
                        {{
                            "Surname": "User Completed",
                            "Forename1": "Some",
                            "Forename2": "Valid",
                            "DOB": "1950-01-29T22:21:21",
                            "Gender": "N",
                            "Address2": "Triumph Boulevard",
                            "PostCode": "H8 3X",
                            "Address1": "12 Harley St",
                            "DateOfHearing": "{}"
                        }}
                    """.format(NOW + 14 * ONE_DAY).replace(
                        "\n", "").replace(" ", ""),
                },
            },

            # TODO: A Case that should be purged since it reached retention policy
            # TODO: A Case that required extended validation to complete
            # TODO: A Case completed in Welsh

        ]

        with open(
            os.path.join(
                ROOT_DIR,
                "cucumber",
                "features",
                "bdd_generated_fixtures.yaml",
            ),
            "w"
        ) as f:
            f.write(
                yaml.dump(
                    FIXTURES_SRC,
                    indent=4,
                    default_flow_style=False))

