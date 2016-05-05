# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0032_auto_20160420_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='enforcement_telephone',
            field=models.CharField(help_text=b'', max_length=255, null=True, verbose_name=b'Telephone number of the enforcement team', blank=True),
        ),
        migrations.AlterField(
            model_name='court',
            name='region_code',
            field=models.CharField(help_text=b'The initial two digit URN number, e.g. 06', max_length=2, verbose_name=b'URN Region Code'),
        ),
    ]
