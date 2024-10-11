# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0034_auto_20160519_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oucode',
            name='ou_code',
            field=models.CharField(help_text='The first five digits of an OU code', unique=True, max_length=5),
        ),
    ]
