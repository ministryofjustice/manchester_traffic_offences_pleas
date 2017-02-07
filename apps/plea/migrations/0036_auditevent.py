# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0035_auto_20160519_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.SmallIntegerField(default=0, choices=[(0, b'not_set'), (1, b'user_journey'), (2, b'case_api'), (3, b'uditevent_api')])),
                ('event_subtype', models.CharField(default=b'', max_length=32)),
                ('event_data', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('extra_data_hash', models.CharField(default=b'', max_length=32)),
                ('event_datetime', models.DateTimeField(auto_now_add=True)),
                ('case', models.ForeignKey(blank=True, to='plea.Case', null=True)),
            ],
        ),
    ]
