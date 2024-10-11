# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0011_court_sjp_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='notice_types',
            field=models.CharField(default='both', help_text='What kind of notices are being sent out by this area?', max_length=7, choices=[('both', 'Both'), ('sjp', 'SJP'), ('non-sjp', 'Non-SJP')]),
        ),
    ]
