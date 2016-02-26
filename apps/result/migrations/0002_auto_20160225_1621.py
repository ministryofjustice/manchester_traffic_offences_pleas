# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='processed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelTable(
            name='result',
            table=None,
        ),
        migrations.AlterModelTable(
            name='resultoffence',
            table=None,
        ),
        migrations.AlterModelTable(
            name='resultoffencedata',
            table=None,
        ),
    ]
