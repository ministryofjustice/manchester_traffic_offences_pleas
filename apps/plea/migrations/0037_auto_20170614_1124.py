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
                help_text=b'Identified the area of the application that the event happened in',
                max_length=255,
                verbose_name=b'event type',
                choices=[
                    (b'not_set', b'Not Set'),
                    (b'case_model', b'Case Save event'),
                    (b'case_form', b'Case Form event'),
                    (b'case_api', b'Case API event'),
                    (b'urn_validator', b'URN validation event'),
                    (b'result_api', b'Result API event'),
                    (b'auditevent_api', b'AuditEvent API event')
                ]
            ),
        ),
    ]
