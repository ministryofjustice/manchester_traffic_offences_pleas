# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0003_courtemailcount_court'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='validate_urn',
            field=models.BooleanField(default=False, help_text=b'Do we have a full set of incoming DX data?'),
        ),
    ]
