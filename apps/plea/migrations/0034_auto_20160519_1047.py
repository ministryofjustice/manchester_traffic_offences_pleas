# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0033_auto_20160505_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='OUCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ou_code', models.CharField(help_text=b'The first 4 digits of an OU code', unique=True, max_length=4)),
            ],
        ),
        migrations.RemoveField(
            model_name='court',
            name='ou_code',
        ),
        migrations.AddField(
            model_name='oucode',
            name='court',
            field=models.ForeignKey(to='plea.Court'),
        ),
    ]
