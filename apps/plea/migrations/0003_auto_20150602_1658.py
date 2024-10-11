# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0002_auto_20150602_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='case_number',
            field=models.CharField(help_text='as supplied by DX', max_length=12, null=True, blank=True),
        ),
    ]
