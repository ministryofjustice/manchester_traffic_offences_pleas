# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0038_auto_20170203_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditevent',
            name='event_trace',
            field=models.CharField(help_text=b'This detail about the reason for this event may be useful for developers to debug import issue', max_length=4000, null=True, verbose_name=b'error detail', blank=True),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='case',
            field=models.ForeignKey(blank=True, to='plea.Case', help_text=b'If there was a successful case loaded then it is related here', null=True, verbose_name=b'related case'),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='event_data',
            field=django.contrib.postgres.fields.hstore.HStoreField(help_text=b'If there was a failure and data fields were found, they are stored here to debug', null=True, verbose_name=b'Event data', blank=True),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='event_datetime',
            field=models.DateTimeField(help_text=b'The time at which the event occurred', verbose_name=b'event date and time', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='event_subtype',
            field=models.CharField(default=b'not_set', help_text=b'The specific reason for the event', max_length=255, verbose_name=b'reason for failure', choices=[(b'not_set', b'Not set'), (b'success', b'Success'), (b'EXT1', b'External failure 1'), (b'EXT2', b'External failure 2'), (b'case_invalid_missing_name', b'Invalid Case: Missing Name'), (b'case_invalid_missing_urn', b'Invalid Case: Missing URN'), (b'case_invalid_name_too_long', b'Invalid Case: Name too long'), (b'case_invalid_offencecode', b'Invalid Case: Invalid offence code'), (b'case_invalid_courtcode', b'Invalid Case: Invalid court code'), (b'case_invalid_not_in_whitelist', b'Invalid Case: Not in whitelist'), (b'case_invalid_duplicate_offence', b'Invalid Case: Duplicate offence')]),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='event_type',
            field=models.CharField(default=b'not_set', help_text=b'Identified the area of the application that the event happened in', max_length=255, verbose_name=b'event type', choices=[(b'not_set', b'Not Set'), (b'case_model', b'Case Save event'), (b'case_form', b'Case Form event'), (b'case_api', b'Case API event'), (b'auditevent_api', b'AuditEvent API enevt')]),
        ),
        migrations.AlterField(
            model_name='auditevent',
            name='extra_data_hash',
            field=models.CharField(default=b'', help_text=b'If the event caused a change to the extra_data then store the hash of it for debugging', max_length=32, verbose_name=b'extra data hash'),
        ),
    ]
