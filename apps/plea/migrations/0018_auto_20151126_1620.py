# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0017_auto_20151126_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultoffence',
            name='result',
            field=models.ForeignKey(related_name='result_offences', to='plea.Result', on_delete=models.CASCADE),
        ),
    ]
