# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20150902_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='userratingaggregate',
            name='question_tag',
            field=models.CharField(default=b'overall', max_length=24),
        ),
        migrations.AddField(
            model_name='userratingaggregate',
            name='question_text',
            field=models.CharField(default='Overall, how satisfied were you with this service?', max_length=255),
            preserve_default=False,
        ),
    ]
