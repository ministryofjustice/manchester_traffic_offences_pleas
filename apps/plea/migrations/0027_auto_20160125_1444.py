# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0026_caseoffencefilter'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='case',
            name='name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='date_of_hearing',
            field=models.DateField(null=True, blank=True),
        ),
    ]
