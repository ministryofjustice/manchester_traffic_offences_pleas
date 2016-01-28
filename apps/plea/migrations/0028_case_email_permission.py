# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0027_auto_20160125_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='email_permission',
            field=models.BooleanField(default=False),
        ),
    ]
