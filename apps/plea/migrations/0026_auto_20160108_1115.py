# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0025_auto_20151210_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='date_of_hearing',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='imported',
            field=models.BooleanField(default=False),
        ),
    ]
