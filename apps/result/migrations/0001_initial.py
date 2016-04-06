# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0030_auto_20160222_1434'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('urn', models.CharField(max_length=30, db_index=True)),
                ('case_number', models.CharField(help_text=b'as supplied by DX', max_length=12, null=True, blank=True)),
                ('ou_code', models.CharField(max_length=10, null=True, blank=True)),
                ('date_of_hearing', models.DateField()),
                ('account_number', models.CharField(max_length=100, null=True, blank=True)),
                ('division', models.CharField(max_length=100, null=True, blank=True)),
                ('instalment_amount', models.CharField(max_length=100, null=True, blank=True)),
                ('lump_sum_amount', models.CharField(max_length=100, null=True, blank=True)),
                ('pay_by_date', models.DateField(null=True, blank=True)),
                ('payment_type', models.CharField(max_length=10, null=True, blank=True)),
                ('sent', models.BooleanField(default=False)),
                ('sent_on', models.DateTimeField(null=True, blank=True)),
                ('case', models.ForeignKey(related_name='results', blank=True, to='plea.Case', null=True)),
            ],
            options={
                'db_table': 'result_result',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultOffence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offence_code', models.CharField(max_length=10, null=True, blank=True)),
                ('offence_seq_number', models.CharField(max_length=10, null=True, blank=True)),
                ('result', models.ForeignKey(related_name='result_offences', to='result.Result')),
            ],
            options={
                'db_table': 'result_resultoffence',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultOffenceData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_code', models.CharField(max_length=10, null=True, blank=True)),
                ('result_short_title', models.CharField(max_length=120)),
                ('result_short_title_welsh', models.CharField(max_length=120, null=True, blank=True)),
                ('result_wording', models.TextField(max_length=4000)),
                ('result_wording_welsh', models.TextField(max_length=4000, null=True, blank=True)),
                ('result_seq_number', models.CharField(max_length=10, null=True, blank=True)),
                ('result_offence', models.ForeignKey(related_name='offence_data', to='result.ResultOffence')),
            ],
            options={
                'db_table': 'result_resultoffencedata',
            },
            bases=(models.Model,),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
