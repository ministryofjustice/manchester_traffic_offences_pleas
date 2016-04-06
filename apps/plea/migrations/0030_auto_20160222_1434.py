# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0029_auto_20160222_1434'),
    ]

    database_operations = [
        migrations.AlterModelTable('Result', 'result_result'),
        migrations.AlterModelTable('ResultOffence', 'result_resultoffence'),
        migrations.AlterModelTable('ResultOffenceData', 'result_resultoffencedata'),
    ]

    state_operations = [
        migrations.DeleteModel('Result'),
        migrations.DeleteModel('ResultOffence'),
        migrations.DeleteModel('ResultOffenceData'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
