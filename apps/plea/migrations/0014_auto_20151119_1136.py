# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from apps.plea.standardisers import standardise_urn


def remove_empty_urns(apps, schema_editor):
    Case = apps.get_model("plea", "Case")
    Case.objects.filter(urn="").delete()


def standardise_urns(apps, schema_editor):
    Case = apps.get_model("plea", "Case")
    for case in Case.objects.all():
        case.urn = standardise_urn(case.urn)
        case.save()


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0013_remove_court_sjp_area'),
    ]

    operations = [
        migrations.RunPython(remove_empty_urns),
        migrations.RunPython(standardise_urns)
    ]
