"""
Fixture Categories
==================

A mixin class for the fixtures command containing the definitions of the data.

To create another one:

 * add a method that returns the data
 * add a parameter, 'count', to that method (you may choose not to honour it)
 * add the initial primary key (pk) offset to PK_OFFSETS

If the fixtures refer to one another, use consistent, object-unique references
and the actual offset pks will be correspondingly related.

 * TODO: Guard against overlap in assigned PKs
"""

import calendar
import datetime
import random
import string

from django.contrib.auth.models import User
from make_a_plea.tests import yield_waffle
from apps.plea.models import INITIATION_TYPE_CHOICES, NOTICE_TYPES_CHOICES
from apps.plea.models import AuditEvent, Case, Court, Offence, OUCode


NOW = datetime.datetime.utcnow()
ONE_DAY = datetime.timedelta(days=1)


class FixtureCategories(object):
    """A mixin class for defining categories (sets) of fixtures"""

    # Keep track of which have been used
    region_codes = []

    # To avoid collisions of fixtures between different categories
    PK_OFFSETS = {
        "core": 1,  # Simple set of fixtures for getting started
        "cucumber": 1000,  # Fixtures required for cucumber journies
        "performance": 1000000,  # Fixtures for prod-like quantities of data
        # performance tests grow most quickly so should have highest pks
    }

    # Valid category arguments
    CATEGORY_ARGS = PK_OFFSETS.keys()

    def init_category(self):
        """Initialise category-related concerns."""

        self.category = getattr(self, self.options["category"])
        self.modelmap = {
            "plea.case": Case,
            "plea.auditevent": AuditEvent,
            "plea.offence": Offence,
            "plea.court": Court,
            "plea.oucode": OUCode,
            "auth.user": User,
        }
        self.pk_offsets = {  # Starting pks for this category of fixtures
            k: self.PK_OFFSETS[self.options["category"]]
            for k in self.modelmap
        }

    def yield_batches(self):
        """Generator to yield batches of the appropriate data"""
        batches, remainder = divmod(self.options["count"], self.BATCH_SIZE)
        for _ in range(batches):
            yield self.category(count=self.BATCH_SIZE)
        if remainder:
            yield self.category(count=remainder)

    def core(self, count):
        """Return a simple set of fixtures required to use the app"""
        # TODO: return some fixtures
        return {
            "plea.case": [],
            "plea.court": [],
            "plea.auditevent": [],
            "plea.offence": [],
        }

    def cucumber(self, count):
        """
        Return fixture data for all cucumber tests. Ignores count parameter.

        This method demonstrates using relative pk offsets while creating the
        data and updating the offsets based on the size of the data created.
        """
        data = {}
        for meth in dir(self):
            if meth.startswith("cucumber_"):
                meth_data = getattr(self, meth)(count)
                for key in meth_data:
                    if key not in data:
                        data[key] = []
                    for item in meth_data[key]:
                        data[key].append(item)
        return data

    def cucumber_users(self, count):
        """Define an admin user for the cucmber tests to use the admin interface"""

        return {
            "auth.user": [
                {
                    "username": "admin",
                    "password": "admin",
                    "email": "root@localhost",
                    "is_superuser": True,
                    "is_staff": True,
                    "is_active": True,
                }
            ]
        }

    def cucumber_duplicate_urns(self, count):
        """Fixtures with duplicate URNs"""

        data = {
            "plea.oucode": [
                {
                    "id": self.pk_offsets["plea.oucode"] + 1,
                    "court": self.pk_offsets["plea.court"] + 1,
                    "ou_code": "11AA1",
                },
                {
                    "id": self.pk_offsets["plea.oucode"] + 2,
                    "court": self.pk_offsets["plea.court"] + 2,
                    "ou_code": "11BB1",
                },
            ],
            "plea.court": [
                # A court that uses strict validation
                {
                    "id": self.pk_offsets["plea.court"] + 1,
                    "court_code": "1234",
                    "region_code": 11,
                    "court_name": 'enforcing test court for duplicate urns',
                    "court_address": ''.join(yield_waffle(words=3, lines=4)),
                    "court_telephone": "1234",
                    "court_email": "nobody@localhost",
                    "court_language": "en",
                    "submission_email": "nobody@localhost",
                    "court_receipt_email": "nobody@localhost",
                    "local_receipt_email": "nobody@localhost",
                    "plp_email": "nobody@localhost",
                    "enabled": True,
                    "test_mode": False,
                    "notice_types": "both",
                    "validate_urn": True,
                    "display_case_data": True,
                    "enforcement_email": "nobody@localhost",
                    "enforcement_telephone": "1234",
                },

                # A court that does not use strict validation
                {
                    "id": self.pk_offsets["plea.court"] + 2,
                    "court_code": "1235",
                    "region_code": 11,
                    "court_name": 'non-enforcing test court for duplicate urns',
                    "court_address": ''.join(yield_waffle(words=3, lines=4)),
                    "court_telephone": "1234",
                    "court_email": "nobody@localhost",
                    "court_language": "en",
                    "submission_email": "nobody@localhost",
                    "court_receipt_email": "nobody@localhost",
                    "local_receipt_email": "nobody@localhost",
                    "plp_email": "nobody@localhost",
                    "enabled": True,
                    "test_mode": False,
                    "notice_types": "both",
                    "validate_urn": False,
                    "display_case_data": True,
                    "enforcement_email": "nobody@localhost",
                    "enforcement_telephone": "1234",
                }
            ],
            "plea.auditevent": [],
            "plea.offence": [],
            "plea.case": []
        }

        # A case for each combination of parameter options
        for init_type in ["J", "R", "O"]:
            for OU_null in [True, False]:
                for sent in [True, False]:
                    for name_match in [True, False]:
                        for postcode_match in [True, False]:
                            for dob_match in [True, False]:
                                for strict in [True, False]:
                                    for OU_match in [True, False]:
                                        for personal in [True, False]:
                                            init_type_weighting = \
                                                int("J" in init_type) * 1 + \
                                                int("R" in init_type) * 2 + \
                                                int("O" in init_type) * 4
                                            urn_part = sum([
                                                init_type_weighting * 256,
                                                OU_null * 128,
                                                sent * 64,
                                                name_match * 32,
                                                postcode_match * 16,
                                                dob_match * 8,
                                                strict * 4,
                                                OU_match * 2,
                                                personal * 1,
                                            ])
                                            urn = "11{court}{urn_part:05d}17".format(
                                                urn_part=urn_part,
                                                court="AA" if strict else "BB",
                                            )

                                            # The case the user is trying to plea
                                            data["plea.case"].append({
                                                "id": self.pk_offsets["plea.case"] + urn_part,
                                                "name": "Case Name",
                                                "urn": urn,
                                                "case_number": 123456,
                                                "email": "root@localhost",
                                                "email_permission": True,
                                                "date_of_hearing": None,
                                                "imported": True,
                                                "ou_code": None if OU_null else "11AA1",
                                                "initiation_type": "O",
                                                "language": "en",
                                                "sent": False,
                                                "processed": False,
                                                "created": NOW - 10 * ONE_DAY,
                                                "completed_on": None,
                                                "extra_data": {
                                                        "Surname": "Name",
                                                        "Forename1": "Case",
                                                        "Forename2": "",
                                                        "DOB": "1950-01-29T22:21:21",
                                                        "Gender": "N",
                                                        "Address2": "Triumph Boulevard",
                                                        "PostCode": "H8 3X",
                                                        "Address1": "319 Harley St",
                                                        "DateOfHearing": "2017-03-29T20:18:28"
                                                    },
                                            })

                                            # A case with the same URN that may cause issues when pleading
                                            data["plea.case"].append({
                                                "id": self.pk_offsets["plea.case"] + urn_part,
                                                "urn": urn,
                                                "name": "Case Name" if name_match else "Different Name",
                                                "case_number": 123456,
                                                "email": "root@localhost",
                                                "email_permission": True,
                                                "date_of_hearing": None,
                                                "imported": True,
                                                "ou_code": None if OU_null else "11AA1" if OU_match else "11BB1",
                                                "initiation_type": "O",
                                                "language": "en",
                                                "sent": sent,
                                                "processed": False,
                                                "created": NOW - 10 * ONE_DAY,
                                                "completed_on": None,
                                                "extra_data": {
                                                        "Surname": "Name",
                                                        "Forename1": "Case" if name_match else "Different",
                                                        "Forename2": "",
                                                        "DOB": "1950-01-29T22:21:21" if dob_match else "1951-01-29T22:21:21",
                                                        "Gender": "N",
                                                        "Address2": "Triumph Boulevard",
                                                        "PostCode": "H8 3X" if postcode_match else "H8 4X",
                                                        "Address1": "319 Harley St",
                                                        "DateOfHearing": "2017-03-29T20:18:28"
                                                    },
                                            })

                                            if not personal:
                                                data["plea.case"][-1]["extra_data"]["OrganisationName"] = "Some Org"
                                                data["plea.case"][-2]["extra_data"]["OrganisationName"] = "Some Org"

        # Deal with the fact the two cases currently have the same id
        case_count = len(data["plea.case"])
        updated_cases = []
        for index, case in enumerate(data["plea.case"]):
            if index % 2 == 0:
                case["id"] += case_count
            updated_cases.append(case)
        data["plea.case"] = updated_cases

        # Add an offence for each case
        for index, case in enumerate(data["plea.case"]):
            data["plea.offence"].append({
                "id": self.pk_offsets["plea.offence"] + index,
                "case_id": case["id"],
                "offence_code": "ZP97",
                "offence_short_title": "Charge of failing to write cucumber tests, fine ${}".format(
                    random.randint(33, 99)),
            })

        # Increment the pk counter for the items we've created
        for model in data:
            self.pk_offsets[model] += len(data[model])

        return data

    def disabled_cucumber_misc(self, count):
        data = {
            "plea.court": [],
            "plea.auditevent": [],
            "plea.offence": [],
            "plea.case": [
                {
                    # A Case ready for a user journey
                    "id": self.pk_offsets["plea.case"],
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
                    "extra_data": {
                            "Surname": "Parker",
                            "Forename1": "Alice",
                            "Forename2": "Alice",
                            "DOB": "1950-01-29T22:21:21",
                            "Gender": "N",
                            "Address2": "Triumph Boulevard",
                            "PostCode": "H8 3X",
                            "Address1": "319 Harley St",
                            "DateOfHearing": "2017-03-29T20:18:28"
                        },
                },

                # A Case that has already been completed
                {
                    "id": self.pk_offsets["plea.case"] + 1,
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
                    "extra_data": {
                            "Surname": "User Completed",
                            "Forename1": "Some",
                            "Forename2": "Valid",
                            "DOB": "1950-01-29T22:21:21",
                            "Gender": "N",
                            "Address2": "Triumph Boulevard",
                            "PostCode": "H8 3X",
                            "Address1": "77 Harley St",
                            "DateOfHearing": None
                        }
                },

                # A Case that has already been completed and resulted
                {
                    "id": self.pk_offsets["plea.case"] + 2,
                    "urn": "00000000003",
                    "name": "Some Valid User Completed Resulted",
                    "case_number": 123458,
                    "email": "root@localhost",
                    "email_permission": True,
                    "date_of_hearing": (NOW + 14 * ONE_DAY).strftime("%Y-%m-%d"),
                    "imported": True,
                    "ou_code": "B01CN02",
                    "initiation_type": "O",
                    "language": "en",
                    "sent": True,
                    "processed": True,
                    "created": NOW - 10 * ONE_DAY,
                    "completed_on": NOW - 5 * ONE_DAY,
                    "extra_data": {
                        "Surname": "User Completed",
                        "Forename1": "Some",
                        "Forename2": "Valid",
                        "DOB": "1950-01-29T22:21:21",
                        "Gender": "N",
                        "Address2": "Triumph Boulevard",
                        "PostCode": "H8 3X",
                        "Address1": "12 Harley St",
                        "DateOfHearing": (NOW + 14 * ONE_DAY).strftime("%Y-%m-%d")
                    },
                }

                # TODO: A Case that is too old to plea
                # TODO: A Case that required extended validation to complete
                # TODO: A Case completed in Welsh
                # TODO: A Case with Offences that have no offence_seq_number
            ]
        }


    def performance(self, count):
        """
        Return count quantities of data for performance testing.

        This method demonstrates incrementing the pk counter throughout rather than at the end.
        """

        data = {
            "plea.auditevent": [],
            "plea.court": [],
            "plea.offence": [],
            "plea.case": [],
        }

        # Some courts for URNs to be associated with...
        court_count = int(self.COURT_FRACTION * count) or 1

        court_pk = self.pk_offsets["plea.court"]
        for court_id in range(court_pk, court_pk + court_count):

            region_code = ''.join([
                str(random.randint(0, 9)),
                str(random.randint(0, 9)),
            ])
            if region_code not in self.region_codes:
                self.region_codes.append(region_code)
            # TODO: Consider courts with duplicate region codes

            data["plea.court"].append({
                "id": court_id,
                "court_code": "BO01NC",
                "region_code": region_code,
                "court_name": ''.join(yield_waffle(words=2)),
                "court_address": ''.join(yield_waffle(words=3, lines=4)),
                "court_telephone": "1234",
                "court_email": "nobody@localhost",
                "court_language": "en",
                "submission_email": "nobody@localhost",
                "court_receipt_email": "nobody@localhost",
                "local_receipt_email": "nobody@localhost",
                "plp_email": "nobody@localhost",
                "enabled": True,
                "test_mode": False,
                "notice_types": random.choice(NOTICE_TYPES_CHOICES)[0],
                "validate_urn": random.choice([True, False]),
                "display_case_data": random.choice([True, False]),
                "enforcement_email": "nobody@localhost",
                "enforcement_telephone": "1234",
            })

        case_pk = self.pk_offsets["plea.case"]
        for case_id in range(case_pk, case_pk + count):
            sent = random.choice([True, False])
            case = {
                "id": case_id,
                "urn": "{0}{1}{2}".format(
                    random.choice(self.region_codes),
                    ''.join(yield_waffle(chars=2)).upper(),
                    random.randrange(1000000, 9999999),
                ),
                "initiation_type": random.choice(INITIATION_TYPE_CHOICES)[0],
                "email": "root@localhost",
                "imported": False,
                "language": random.choice(["en", "en", "en", "cy"]),
                "name": ''.join(
                    random.choice(string.ascii_lowercase)
                    for _ in range(15)),
                "extra_data": {},
                "sent": sent,
            }
            if sent:
                case["completed_on"] = datetime.datetime.fromtimestamp(
                    random.randint(  # Some time in the last two weeks
                        calendar.timegm(NOW.timetuple()) - (14 * ONE_DAY).total_seconds(),
                        calendar.timegm(NOW.timetuple()),
                    ))
            data["plea.case"].append(case)

            # Some offenses to go with these cases...
            for offenceid in range(random.randint(0, 9)):
                data["plea.offence"].append({
                    "id": self.pk_offsets["plea.offence"],
                    "offence_seq_number": offenceid,
                    "case_id": case_id,
                    "offence_wording": "Test offence ${0}".format(random.randint(1, 200)),
                })
                self.pk_offsets["plea.offence"] += 1

            # Extra items to create sometimes...
            if case_id % 10 == 0:

                data["plea.auditevent"].append({
                    "id": self.pk_offsets["plea.auditevent"],
                    "event_type": "case_model",
                    "event_subtype": "success",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "test common extra event for a case",
                    "case": case_id,
                })
                self.pk_offsets["plea.auditevent"] += 1

                data["plea.auditevent"].append({
                    "id": self.pk_offsets["plea.auditevent"],
                    "event_type": "case_form",
                    "event_subtype": "case_invalid_invalid_urn",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "Test event with no case",
                    "case": None,
                })
                self.pk_offsets["plea.auditevent"] += 1

            if case_id % 100 == 0:
                data["plea.auditevent"].append({
                    "id": self.pk_offsets["plea.auditevent"],
                    "event_type": "case_model",
                    "event_subtype": "case_invalid_missing_urn",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "test rare extra event for a case",
                    "case": case_id,
                })
                self.pk_offsets["plea.auditevent"] += 1

        return data
