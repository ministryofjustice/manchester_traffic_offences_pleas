# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0030_auto_20160222_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
