# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0036_auditevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditevent',
            name='event_type',
            field=models.CharField(
                help_text='Identified the area of the application that the event happened in',
                max_length=255,
                verbose_name='event type',
                choices=[
                    ('not_set', 'Not Set'),
                    ('case_model', 'Case Save event'),
                    ('case_form', 'Case Form event'),
                    ('case_api', 'Case API event'),
                    ('urn_validator', 'URN validation event'),
                    ('result_api', 'Result API event'),
                    ('auditevent_api', 'AuditEvent API event')
                ]
            ),
        ),
    ]
