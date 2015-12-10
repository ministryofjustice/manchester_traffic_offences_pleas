# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_initiation_type(apps, schema_editor):
    Case = apps.get_model("plea", "Case")
    for case in Case.objects.filter(initiation_type="C"):
        case.initiation_type = "Q"
        case.save()


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0024_auto_20151210_1525'),
    ]

    operations = [
        migrations.RunPython(update_initiation_type)
    ]
