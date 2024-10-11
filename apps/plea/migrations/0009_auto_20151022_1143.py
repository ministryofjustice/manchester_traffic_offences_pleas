# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0008_auto_20151021_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='language',
            field=models.CharField(default=b'en', max_length=2, choices=[(b'en', b'English'), (b'cy', b'Welsh')]),
        ),
        migrations.AddField(
            model_name='courtemailcount',
            name='language',
            field=models.CharField(default=b'en', max_length=2, choices=[(b'en', b'English'), (b'cy', b'Welsh')]),
        ),
        migrations.AlterField(
            model_name='case',
            name='initiation_type',
            field=models.CharField(default=b'C', max_length=2, choices=[(b'C', b'Charge'), (b'J', b'SJP'), (b'Q', b'Requisition'), (b'O', b'Other'), (b'R', b'Remitted'), (b'S', b'Summons')]),
        ),
        migrations.AlterField(
            model_name='courtemailcount',
            name='court',
            field=models.ForeignKey(related_name='court_email_counts', to='plea.Court', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='courtemailcount',
            name='initiation_type',
            field=models.CharField(default=b'C', max_length=2, choices=[(b'C', b'Charge'), (b'J', b'SJP'), (b'Q', b'Requisition'), (b'O', b'Other'), (b'R', b'Remitted'), (b'S', b'Summons')]),
        ),
    ]
