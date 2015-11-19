# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0012_court_notice_types'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='court',
            name='sjp_area',
        ),
    ]
