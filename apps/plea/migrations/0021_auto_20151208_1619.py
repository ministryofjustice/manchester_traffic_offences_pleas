# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0020_auto_20151201_1134'),
    ]

    operations = [

        migrations.AddField(
            model_name='result',
            name='sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='result',
            name='sent_on',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
