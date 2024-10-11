# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0010_auto_20151029_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='sjp_area',
            field=models.BooleanField(default=False, help_text='Is this area sending out SJP notices?'),
        ),
    ]
