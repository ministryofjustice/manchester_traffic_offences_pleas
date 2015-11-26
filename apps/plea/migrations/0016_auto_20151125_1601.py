# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0015_datavalidation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datavalidation',
            name='date_entered',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
