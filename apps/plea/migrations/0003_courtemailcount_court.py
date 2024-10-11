# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0002_auto_20150518_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtemailcount',
            name='court',
            field=models.ForeignKey(default=1, to='plea.Court', on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
