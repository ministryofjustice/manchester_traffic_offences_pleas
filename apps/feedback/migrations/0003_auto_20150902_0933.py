# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_auto_20150603_1259'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userrating',
            old_name='rating',
            new_name='service_rating',
        ),
        migrations.AddField(
            model_name='userrating',
            name='call_centre_rating',
            field=models.PositiveIntegerField(null=True, choices=[(5, 'very satisfied'), (4, 'satisfied'), (3, 'neither satisfied nor dissatisfied'), (2, 'dissatisfied'), (1, 'very dissatisfied')]),
        ),
    ]
