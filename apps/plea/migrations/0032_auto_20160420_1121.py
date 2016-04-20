# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0031_case_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='completed_on',
            field=models.DateTimeField(help_text=b'The date/time a user completes a submission.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='court',
            name='enforcement_email',
            field=models.CharField(help_text=b'', max_length=255, null=True, verbose_name=b'Email address of the enforcement team', blank=True),
        ),
        migrations.AddField(
            model_name='court',
            name='enforcement_telephone',
            field=models.CharField(help_text=b'', max_length=255, null=True, verbose_name=b'Email address of the enforcement team', blank=True),
        ),
        migrations.AddField(
            model_name='court',
            name='ou_code',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
