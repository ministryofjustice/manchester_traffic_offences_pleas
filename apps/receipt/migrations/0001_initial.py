# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiptLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Error'), (1, 'Completed')])),
                ('started', models.DateTimeField(help_text='The time the script started processing', auto_now=True)),
                ('run_time', models.PositiveIntegerField(help_text='Time the script took to complete in seconds', null=True, blank=True)),
                ('query_from', models.DateTimeField(null=True, blank=True)),
                ('query_to', models.DateTimeField(null=True, blank=True)),
                ('total_emails', models.PositiveIntegerField(default=0, help_text='Number of entries received from the API')),
                ('total_errors', models.PositiveIntegerField(default=0, help_text='Number of entries that were not processable')),
                ('total_failed', models.PositiveIntegerField(default=0, help_text='Number of entries recorded as failed by the PA')),
                ('total_success', models.PositiveIntegerField(default=0, help_text='Number of entries that the PA indicated were successfully processed')),
                ('status_detail', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
