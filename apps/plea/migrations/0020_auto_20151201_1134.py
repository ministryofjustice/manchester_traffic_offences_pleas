# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0019_result_urn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='forenames',
        ),
        migrations.RemoveField(
            model_name='case',
            name='name',
        ),
        migrations.RemoveField(
            model_name='case',
            name='surname',
        ),
        migrations.RemoveField(
            model_name='case',
            name='title',
        ),
        HStoreExtension(),
        migrations.AddField(
            model_name='case',
            name='extra_data',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True),
        ),
    ]
