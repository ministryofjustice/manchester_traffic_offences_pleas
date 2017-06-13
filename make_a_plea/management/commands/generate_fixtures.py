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
import random
import string
import yaml

from django.core.management.base import BaseCommand

from apps.plea.models import AuditEvent, Case, INITIATION_TYPE_CHOICES, Offence


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))


class Command(BaseCommand):

    help = """Generate or install fixtures."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate_dynamic',
            action='store_true',
            dest="dynamic",
            default=False)
        parser.add_argument(
            '--install_performance',
            action='store_true',
            dest="performance",
            default=False)
        parser.add_argument(
            '--fixture_count',
            action='store',
            dest="fixture_count",
            default=10000)

    def handle(self, *args, **options):

        if "performance" in options:
            self._install_performance(
                fixture_count=int(options["fixture_count"]))

        if "dynamic" in options:
            self._generate_dynamic()

    def _save_fixturefile(self, filepath, data):

        with open(
            os.path.join(
                ROOT_DIR,
                "cucumber",
                "features",
                filepath,
            ),
            "w"
        ) as f:
            f.write(
                yaml.dump(
                    data,
                    indent=4,
                    default_flow_style=False))

    def _install_performance(self, fixture_count):
        """Insert large quantities of data for performance testing"""
        for x in range(fixture_count):
            params = {
                "urn": "{0}{1}{2}".format(
                    "".join(
                        random.choice(string.ascii_uppercase)
                        for _ in range(2)),
                    random.choice(["00", "50", "51", "99"]),
                    random.randrange(1000000, 9999999),
                ),
                "initiation_type": random.choice(INITIATION_TYPE_CHOICES)[0],
                "email": "root@localhost",
                "imported": False,
                "name": ''.join(
                    random.choice(string.ascii_lowercase)
                    for _ in range(15)),
                "extra_data": {},
            }
            case = Case(**params)
            case.save()
            for x in range(1, random.randint(1, 10)):
                Offence(**{
                    "case_id": case.id,
                    "offence_wording": "Test offence ${0}".format(random.randint(1, 200)),
                }).save()

            # Extra items to create sometimes
            if x % 10 == 0:
                AuditEvent().populate(
                    event_type="case_model",
                    event_subtype="success",
                    event_trace="test common extra event for a case",
                    case=case,
                )
                AuditEvent().populate(
                    event_type="case_form",
                    event_subtype="case_invalid_invalid_urn",
                    event_trace="Test event with no case",
                )

            if x % 100 == 0:
                AuditEvent().populate(
                    event_type="case_model",
                    event_subtype="case_invalid_missing_urn",
                    event_trace="test rare extra event for a case",
                    case=case,
                )

    def _generate_dynamic(self):
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

        self._save_fixturefile(
            "bdd_generated_fixtures.yaml",
            FIXTURES_SRC,
        )
