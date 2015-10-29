# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0009_auto_20151022_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='urn',
            field=models.CharField(max_length=30, db_index=True),
        ),
    ]
