# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0035_auto_20160519_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name=b'Audit Event ID', primary_key=True)),
                ('event_type', models.CharField(help_text=b'Identified the area of the application that the event happened in', max_length=255, verbose_name=b'event type', choices=[(b'not_set', b'Not Set'), (b'case_model', b'Case Save event'), (b'case_form', b'Case Form event'), (b'case_api', b'Case API event'), (b'result_api', b'Result API event'), (b'auditevent_api', b'AuditEvent API event')])),
                ('event_subtype', models.CharField(help_text=b'The specific reason for the event', max_length=255, verbose_name=b'reason for failure', choices=[(b'not_set', b'Not set'), (b'success', b'Success'), (b'EXT1', b'External failure 1'), (b'EXT2', b'External failure 2'), (b'case_strict_validation_failed', b'Form Validation Error: Strict'), (b'case_loose_validation_failed', b'Form Validation Error: Loose'), (b'case_invalid_missing_name', b'Invalid Case: Missing Name'), (b'case_invalid_missing_urn', b'Invalid Case: Missing URN'), (b'case_invalid_invalid_urn', b'Invalid Case: Invalid URN'), (b'case_invalid_missing_dateofhearing', b'Invalid Case: Missing date of hearing'), (b'case_invalid_name_too_long', b'Invalid Case: Name too long'), (b'case_invalid_offencecode', b'Invalid Case: Invalid offence code'), (b'case_invalid_courtcode', b'Invalid Case: Invalid court code'), (b'case_invalid_not_in_whitelist', b'Invalid Case: Not in whitelist'), (b'case_invalid_duplicate_offence', b'Invalid Case: Duplicate offence'), (b'case_invalid_duplicate_urn_used', b'Invalid Case: Duplicate URN already used (sent)'), (b'case_invalid_no_offences', b'Invalid Case: No offences'), (b'result_invalid_duplicate_urn_used', b'Invalid Result: Duplicate URN already used (sent)')])),
                ('event_trace', models.CharField(help_text=b'This detail about the reason for this event may be useful for developers to debug import issue', max_length=4000, null=True, verbose_name=b'error detail', blank=True)),
                ('event_data', django.contrib.postgres.fields.hstore.HStoreField(help_text=b'If there was a failure and data fields were found, they are stored here to debug', null=True, verbose_name=b'Event data', blank=True)),
                ('event_datetime', models.DateTimeField(help_text=b'The time at which the event occurred', verbose_name=b'event date and time', auto_now_add=True)),
                ('case', models.ForeignKey(blank=True, to='plea.Case', help_text=b'If there was a successful case loaded then it is related here', null=True, verbose_name=b'Related case', on_delete=models.CASCADE)),
            ],
        ),
    ]
