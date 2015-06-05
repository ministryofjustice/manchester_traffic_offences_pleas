# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userratingaggregate',
            name='feedback_avg',
        ),
        migrations.RemoveField(
            model_name='userratingaggregate',
            name='feedback_count',
        ),
        migrations.RemoveField(
            model_name='userratingaggregate',
            name='feedback_total',
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='rating_1',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='rating_2',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='rating_3',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='rating_4',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='rating_5',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='total',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
