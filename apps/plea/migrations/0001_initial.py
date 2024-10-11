# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('urn', models.CharField(max_length=16, db_index=True)),
                ('title', models.CharField(max_length=35, null=True, blank=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('forenames', models.CharField(help_text='as supplied by DX', max_length=105, null=True, blank=True)),
                ('surname', models.CharField(help_text='as supplied by DX', max_length=35, null=True, blank=True)),
                ('case_number', models.CharField(help_text='as supplied by DX', max_length=10, null=True, blank=True)),
                ('sent', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CaseAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=50)),
                ('status_info', models.TextField(null=True, blank=True)),
                ('case', models.ForeignKey(related_name='actions', to='plea.Case', on_delete=models.CASCADE)),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('court_code', models.CharField(max_length=100, null=True, blank=True)),
                ('region_code', models.CharField(help_text='The initial two digit URN number, e.g. 06', unique=True, max_length=2)),
                ('court_name', models.CharField(max_length=255)),
                ('court_address', models.TextField()),
                ('court_telephone', models.CharField(max_length=50)),
                ('court_email', models.CharField(help_text='A user facing email address', max_length=255)),
                ('submission_email', models.CharField(help_text='The outbound court email used to send submission data', max_length=255)),
                ('court_receipt_email', models.CharField(help_text='The email address the court uses to send receipt emails to MaP', max_length=255, null=True, blank=True)),
                ('local_receipt_email', models.CharField(help_text='The inbound receipt email address. Used for validation purposes.', max_length=255, null=True, blank=True)),
                ('plp_email', models.CharField(help_text=b"The PLP outbound email - if left empty the PLP email won't be sent", max_length=255, null=True, blank=True)),
                ('enabled', models.BooleanField(default=False)),
                ('test_mode', models.BooleanField(default=False, help_text='Is this court entry used for testing purposes?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourtEmailCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('total_pleas', models.IntegerField()),
                ('total_guilty', models.IntegerField()),
                ('total_not_guilty', models.IntegerField()),
                ('hearing_date', models.DateTimeField()),
                ('sc_guilty_char_count', models.PositiveIntegerField(default=0)),
                ('sc_not_guilty_char_count', models.PositiveIntegerField(default=0)),
                ('sent', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ou_code', models.CharField(max_length=10, null=True, blank=True)),
                ('offence_code', models.CharField(max_length=10, null=True, blank=True)),
                ('offence_short_title', models.CharField(max_length=100)),
                ('offence_wording', models.TextField(max_length=4000)),
                ('offence_seq_number', models.CharField(max_length=10, null=True, blank=True)),
                ('case', models.ForeignKey(related_name='offences', to='plea.Case', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UsageStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('online_submissions', models.PositiveIntegerField(default=0)),
                ('online_guilty_pleas', models.PositiveIntegerField(default=0)),
                ('online_not_guilty_pleas', models.PositiveIntegerField(default=0)),
                ('postal_requisitions', models.PositiveIntegerField(null=True, blank=True)),
                ('postal_responses', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('start_date',),
                'verbose_name_plural': 'Usage Stats',
            },
            bases=(models.Model,),
        ),
    ]
