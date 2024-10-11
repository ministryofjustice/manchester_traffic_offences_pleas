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
                ('id', models.AutoField(serialize=False, verbose_name='Audit Event ID', primary_key=True)),
                ('event_type', models.CharField(help_text='Identified the area of the application that the event happened in', max_length=255, verbose_name='event type', choices=[('not_set', 'Not Set'), ('case_model', 'Case Save event'), ('case_form', 'Case Form event'), ('case_api', 'Case API event'), ('result_api', 'Result API event'), ('auditevent_api', 'AuditEvent API event')])),
                ('event_subtype', models.CharField(help_text='The specific reason for the event', max_length=255, verbose_name='reason for failure', choices=[('not_set', 'Not set'), ('success', 'Success'), ('EXT1', 'External failure 1'), ('EXT2', 'External failure 2'), ('case_strict_validation_failed', 'Form Validation Error: Strict'), ('case_loose_validation_failed', 'Form Validation Error: Loose'), ('case_invalid_missing_name', 'Invalid Case: Missing Name'), ('case_invalid_missing_urn', 'Invalid Case: Missing URN'), ('case_invalid_invalid_urn', 'Invalid Case: Invalid URN'), ('case_invalid_missing_dateofhearing', 'Invalid Case: Missing date of hearing'), ('case_invalid_name_too_long', 'Invalid Case: Name too long'), ('case_invalid_offencecode', 'Invalid Case: Invalid offence code'), ('case_invalid_courtcode', 'Invalid Case: Invalid court code'), ('case_invalid_not_in_whitelist', 'Invalid Case: Not in whitelist'), ('case_invalid_duplicate_offence', 'Invalid Case: Duplicate offence'), ('case_invalid_duplicate_urn_used', 'Invalid Case: Duplicate URN already used (sent)'), ('case_invalid_no_offences', 'Invalid Case: No offences'), ('result_invalid_duplicate_urn_used', 'Invalid Result: Duplicate URN already used (sent)')])),
                ('event_trace', models.CharField(help_text='This detail about the reason for this event may be useful for developers to debug import issue', max_length=4000, null=True, verbose_name='error detail', blank=True)),
                ('event_data', django.contrib.postgres.fields.hstore.HStoreField(help_text='If there was a failure and data fields were found, they are stored here to debug', null=True, verbose_name='Event data', blank=True)),
                ('event_datetime', models.DateTimeField(help_text='The time at which the event occurred', verbose_name='event date and time', auto_now_add=True)),
                ('case', models.ForeignKey(blank=True, to='plea.Case', help_text='If there was a successful case loaded then it is related here', null=True, verbose_name='Related case', on_delete=models.CASCADE)),
            ],
        ),
    ]
