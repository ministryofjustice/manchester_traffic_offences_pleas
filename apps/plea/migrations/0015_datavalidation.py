# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0014_auto_20151119_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataValidation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_entered', models.DateTimeField(auto_created=True)),
                ('urn_entered', models.CharField(max_length=50)),
                ('urn_standardised', models.CharField(max_length=50)),
                ('urn_formatted', models.CharField(max_length=50)),
                ('case_match_count', models.PositiveIntegerField(default=0)),
                ('case_match', models.ForeignKey(blank=True, to='plea.Case', null=True, on_delete=models.CASCADE)),
            ],
        ),
    ]
