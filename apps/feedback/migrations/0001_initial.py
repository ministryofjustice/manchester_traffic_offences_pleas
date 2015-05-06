# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('rating', models.PositiveIntegerField(choices=[(5, 'very satisfied'), (4, 'satisfied'), (3, 'neither satisfied nor dissatisfied'), (2, 'dissatisfied'), (1, 'very dissatisfied')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRatingAggregate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('feedback_count', models.PositiveIntegerField()),
                ('feedback_total', models.PositiveIntegerField()),
                ('feedback_avg', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
                'ordering': ('start_date',),
            },
            bases=(models.Model,),
        ),
    ]
