"""
Fixture Categories
==================

A mixin class for the fixtures command containing the definitions of the data.

To create another one:

 * add a method that returns the data
 * add a parameter, count, to that method (you may choose not to honour it)
 * add the primary key (pk) offset to PK_OFFSETS

If the fixtures refer to one another, use consistent, object-unique references
and the actual offset pks will be correspondingly related.

"""
import calendar
import datetime
import random
import string

from make_a_plea.tests import yield_waffle
from apps.plea.models import INITIATION_TYPE_CHOICES, NOTICE_TYPES_CHOICES


NOW = datetime.datetime.utcnow()
ONE_DAY = datetime.timedelta(days=1)

#a = calendar.timegm(NOW.timetuple()) - (14 * ONE_DAY).total_seconds()
#print a
#exit(1)

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
        """Not a dunder method as it must be called from django's handle()"""

        self.category = getattr(self, self.options["category"])
        self.pk_offsets = {  # Starting pks for this category of fixtures
            k: self.PK_OFFSETS[self.options["category"]]
            for k in [
                "auditevent",
                "case",
                "court",
                "offence",
            ]
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
        # TODO: implement!
        return {
            "case": [],
            "court": [],
            "auditevent": [],
            "offence": [],
        }

    def cucumber(self, count):
        """Return fixture data for cucumber tests. Ignores count parameter."""

        data = {
            "court": [],
            "auditevent": [],
            "offence": [],
            "case": [
                {
                    # A Case ready for a user journey
                    "id": 1,
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

                # A Case that has already been completed
                {
                    "id": 2,
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

                # A Case that has already been completed and resulted
                {
                    "id": 3,
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

                # TODO: A Case that is too old to plea
                # TODO: A Case that required extended validation to complete
                # TODO: A Case completed in Welsh
            ]
        }

        return data

    def performance(self, count):
        """Return count quantities of data for performance testing"""
        data = {
            "auditevent": [],
            "court": [],
            "offence": [],
            "case": [],
        }

        # Some courts for URNs to be associated with...
        court_count = int(sum([
            1,  # At least one
            self.COURT_FRACTION * count,  # A fraction of count
        ]))

        for courtid in range(court_count):

            region_code = ''.join([
                str(random.randint(0, 9)),
                str(random.randint(0, 9)),
            ])
            if region_code not in self.region_codes:
                self.region_codes.append(region_code)
            # TODO: Consider courts with duplicate region codes

            data["court"].append({
                "id": courtid,
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

        for caseid in range(1, count + 1):
            sent = random.choice([True, False])
            case = {
                "id": caseid,
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
            data["case"].append(case)

            # Some offenses to go with these cases...
            for offenceid in range(1, random.randint(1, 10)):
                data["offence"].append({
                    "id": offenceid,
                    "offence_seq_number": offenceid,
                    "case_id": caseid,
                    "offence_wording": "Test offence ${0}".format(random.randint(1, 200)),
                })

            # Extra items to create sometimes...
            if caseid % 10 == 0:
                data["auditevent"].append({
                    "event_type": "case_model",
                    "event_subtype": "success",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "test common extra event for a case",
                    "case": caseid,
                })
                data["auditevent"].append({
                    "event_type": "case_form",
                    "event_subtype": "case_invalid_invalid_urn",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "Test event with no case",
                    "case": None,
                })

            if caseid % 100 == 0:
                data["auditevent"].append({
                    "event_type": "case_model",
                    "event_subtype": "case_invalid_missing_urn",
                    "event_datetime": datetime.datetime.utcnow(),
                    "event_trace": "test rare extra event for a case",
                    "case": caseid,
                })

        return data
