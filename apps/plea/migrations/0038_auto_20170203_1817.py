# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0037_auto_20170131_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditevent',
            name='event_type',
            field=models.SmallIntegerField(default=0, choices=[(0, b'not_set'), (1, b'case_model'), (2, b'case_form'), (3, b'case_api'), (4, b'auditevent_api')]),
        ),
    ]
