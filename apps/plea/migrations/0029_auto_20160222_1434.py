# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0028_case_email_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='court_email',
            field=models.CharField(help_text='The email address for users to contact the court', max_length=255),
        ),
        migrations.AlterField(
            model_name='court',
            name='court_receipt_email',
            field=models.CharField(help_text='The email address to send receipts confirming the plea has been filed correctly', max_length=255, null=True, verbose_name='Plea receipt email', blank=True),
        ),
        migrations.AlterField(
            model_name='court',
            name='enabled',
            field=models.BooleanField(default=False, verbose_name='Live'),
        ),
        migrations.AlterField(
            model_name='court',
            name='plp_email',
            field=models.CharField(help_text='The email address provided by the police to receive pleas', max_length=255, null=True, verbose_name='Police submission email', blank=True),
        ),
        migrations.AlterField(
            model_name='court',
            name='region_code',
            field=models.CharField(help_text='The initial two digit URN number, e.g. 06', unique=True, max_length=2, verbose_name='URN Region Code'),
        ),
        migrations.AlterField(
            model_name='court',
            name='submission_email',
            field=models.CharField(help_text='The outbound court email used to send submission data', max_length=255, verbose_name='Internal contact details'),
        ),
    ]
