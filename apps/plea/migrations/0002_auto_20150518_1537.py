# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offence',
            name='ou_code',
        ),
        migrations.AddField(
            model_name='case',
            name='ou_code',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='case_number',
            field=models.CharField(help_text='as supplied by DX', max_length=12, null=True, blank=True),
        ),
    ]
