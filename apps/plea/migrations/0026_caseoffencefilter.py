# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0026_auto_20160108_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseOffenceFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filter_match', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
            ],
        ),
    ]
