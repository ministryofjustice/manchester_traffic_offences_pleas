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
            field=models.CharField(default='en', max_length=2, choices=[('en', 'English'), ('cy', 'Welsh')]),
        ),
        migrations.AddField(
            model_name='courtemailcount',
            name='language',
            field=models.CharField(default='en', max_length=2, choices=[('en', 'English'), ('cy', 'Welsh')]),
        ),
        migrations.AlterField(
            model_name='case',
            name='initiation_type',
            field=models.CharField(default='C', max_length=2, choices=[('C', 'Charge'), ('J', 'SJP'), ('Q', 'Requisition'), ('O', 'Other'), ('R', 'Remitted'), ('S', 'Summons')]),
        ),
        migrations.AlterField(
            model_name='courtemailcount',
            name='court',
            field=models.ForeignKey(related_name='court_email_counts', to='plea.Court', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='courtemailcount',
            name='initiation_type',
            field=models.CharField(default='C', max_length=2, choices=[('C', 'Charge'), ('J', 'SJP'), ('Q', 'Requisition'), ('O', 'Other'), ('R', 'Remitted'), ('S', 'Summons')]),
        ),
    ]
