# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-20 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0004_auto_20150902_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrating',
            name='comments',
            field=models.CharField(blank=True, default=None, max_length=4000, null=True),
        ),
    ]
