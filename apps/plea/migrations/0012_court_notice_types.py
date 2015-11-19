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
            field=models.CharField(default=b'both', help_text=b'What kind of notices are being sent out by this area?', max_length=7, choices=[(b'both', b'Both'), (b'sjp', b'SJP'), (b'non-sjp', b'Non-SJP')]),
        ),
    ]
