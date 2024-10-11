# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0006_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='display_case_data',
            field=models.BooleanField(default=False, help_text='Display the updated plea page for cases that have offence data attached'),
        ),
    ]
