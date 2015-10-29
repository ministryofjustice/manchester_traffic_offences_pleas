# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0007_auto_20150902_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='initiation_type',
            field=models.CharField(default=b'C', max_length=2),
        ),
        migrations.AddField(
            model_name='court',
            name='court_language',
            field=models.CharField(default=b'en', max_length=4, choices=[(b'en', b'English'), (b'cy', b'Welsh')]),
        ),
        migrations.AddField(
            model_name='courtemailcount',
            name='initiation_type',
            field=models.CharField(default=b'C', max_length=2),
        ),
        migrations.AddField(
            model_name='offence',
            name='offence_short_title_welsh',
            field=models.CharField(max_length=120, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='offence',
            name='offence_wording_welsh',
            field=models.TextField(max_length=4000, null=True, blank=True),
        ),
    ]
