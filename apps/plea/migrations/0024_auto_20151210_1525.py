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
            field=models.CharField(default=b'Q', max_length=2, choices=[(b'C', b'Charge'), (b'J', b'SJP'), (b'Q', b'Requisition'), (b'O', b'Other'), (b'R', b'Remitted'), (b'S', b'Summons')]),
        ),
    ]
