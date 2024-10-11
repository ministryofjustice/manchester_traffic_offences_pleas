# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0023_auto_20151210_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='initiation_type',
            field=models.CharField(default='Q', max_length=2, choices=[('C', 'Charge'), ('J', 'SJP'), ('Q', 'Requisition'), ('O', 'Other'), ('R', 'Remitted'), ('S', 'Summons')]),
        ),
    ]
