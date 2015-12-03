# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0018_auto_20151126_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='urn',
            field=models.CharField(default='', max_length=30, db_index=True),
            preserve_default=False,
        ),
    ]
