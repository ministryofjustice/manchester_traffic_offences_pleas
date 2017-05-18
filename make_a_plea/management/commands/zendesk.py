"""
Config
======

Create a file at ~/.hmcts-zendesk with the content like this:

url: "https://ministryofjustice.zendesk.com"
email: "team.player@hmcts.net"
password: "my-h$rd-2-GuEsS-P@55w0rd"
out_file: "~/zendump.csv"
raw_queries:
  - "?query=type:ticket tags:makeaplea"
  #- "?query=type:ticket -tags:plea_receipt -description:\"Used the call centre\" -description:\"Service satisfaction\""
  #- "?query=type:ticket -tags:plea_receipt -description:\"Used the call centre\" -description:\"Comments -\""

Usage
=====

./manage.py zendesk --to-csv

bugs and limitations
====================

   * Where 'received_at:makeaplea@ministryofjustice.zendesk.com' is used in
   the web query builder, it is not clear from which field this derives, nor
   does it appear possible to search on subkeys on the 'via' field. Also,
   'recipient' is not the field as there are too few results. We could post-
   process to fix this, currently the results ignore this filter.
   * There is no de-duplication between filters
   * There is no separation of filters into different files
   * zdesk failed (subjects were often truncated) when used in normal mode.
   Since raw_queries are now required and the caching is of little use to us
   for this task we could switch out to just requests.

"""

import codecs
import csv
import cStringIO
import os
from optparse import make_option
import re
import yaml


from django.core.management.base import BaseCommand
from zdesk import Zendesk


# Most fields are simple scalars. Fields should only be in one list.
SIMPLE_FIELDS = [
    u'id',
    u'status',
    u'created_at',
    u'updated_at',
    u'due_at',
    u'group_id',
    u'has_incidents',
    u'is_public',
    u'organization_id',
    u'priority',
    u'problem_id',
    u'recipient',
    u'requester_id',
    u'satisfaction_rating',
    u'status',
    u'submitter_id',
    u'type',
    u'url',
    u'result_type',
    u'allow_channelback',
    u'assignee_id',
    u'brand_id',
]

# Some have structure like dicts or lists that will be strigified
STRUCTURED_FIELDS = [
    u'tags',
    u'external_id',
    u'fields',
    u'forum_topic_id',
    u'followup_ids',
    u'collaborator_ids',
    u'custom_fields',
    u'sharing_agreement_ids',
    u'via',
]

# Some may contain various line endings that will be coerced to \n
NEWLINE_FIELDS = [
    "description",
    "subject",
    "raw_subject",
]


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--to-csv',
            action='store_true',
            dest='to-csv',
            default=False,
            help='Export all relevant zendesk items to csv file'),
        )

    def handle(self, *args, **options):
        self.load_settings()
        self.init_zen()

        if options["to-csv"]:
            self.to_csv()

    def load_settings(self):
        with open(os.path.expanduser("~/.hmcts-zendesk"), "r") as config_file:
            self.settings = yaml.load(config_file.read())

    def init_csv(self, f, dialect=csv.excel):
        self.writer = csv.writer(f, dialect=dialect)

    def init_zen(self):
        self.zendesk = Zendesk(
            self.settings["url"],
            self.settings["email"],
            self.settings["password"])

    def get_all_fieldnames(self):
        return \
            SIMPLE_FIELDS + \
            NEWLINE_FIELDS + \
            STRUCTURED_FIELDS

    def to_csv(self):
        self.outfile = self.settings.get('outfile', 'zendump.csv')
        self.batch_size = 100
        with open(self.outfile, "wb") as f:

            self.init_csv(f)
            self.writerow(self.get_all_fieldnames())  # CSV Header

            for batch in self.yield_ticket_batches():
                for ticket in batch:
                    self.writerow(self.ticket_to_row(ticket))

    def writerow(self, row):
        self.writer.writerow([
            cell.encode("utf-8")
            for cell in row])

    def ticket_to_row(self, ticket):
        return \
            self.get_simple_fields(ticket) + \
            self.get_newline_fields(ticket) + \
            self.get_structured_fields(ticket)

    def parse_simple_field(self, field):
        try:
            return field.encode("utf-8")
        except AttributeError:  # ints
            return str(field).encode("utf-8")

    def get_simple_fields(self, ticket):
        fields = []
        for field in SIMPLE_FIELDS:
            if field in ticket:
                fields.append(self.parse_simple_field(ticket[field]))
            else:
                fields.append("")
        return fields

    def parse_newline_field(self, field):
        return field or ""

    def get_newline_fields(self, ticket):
        fields = []
        for field in NEWLINE_FIELDS:
            if field in ticket and field is not None:
                fields.append(self.parse_newline_field(ticket[field]))
            else:
                fields.append("")
        return fields

    def parse_structured_field(self, field):
        return str(field)

    def get_structured_fields(self, ticket):
        fields = []
        for field in STRUCTURED_FIELDS:
            if field in ticket:
                fields.append(self.parse_structured_field(ticket[field]))
            else:
                fields.append("")
        return fields

    def yield_ticket_batches(self):
        """Generates batches of tickets"""

        for raw_query in self.settings["raw_queries"]:

            first_page = self.zendesk.search(raw_query=raw_query)
            yield first_page["results"]

            count = first_page["count"]
            print "{} tickets from ZenDesk match filter.".format(count)
            page_count, remainder = divmod(count, self.batch_size)
            page_count = page_count + 1 if remainder else page_count

            for page_id in range(1, page_count):
                qpage = " page:{}".format(page_id)
                page = self.zendesk.search(raw_query=raw_query + qpage)
                yield page["results"]
