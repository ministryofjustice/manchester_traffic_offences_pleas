# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0002_auto_20160225_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
