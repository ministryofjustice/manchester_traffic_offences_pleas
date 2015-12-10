# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from apps.plea.standardisers import standardise_urn


def standardise_urns(apps, schema_editor):
    Case = apps.get_model("plea", "Case")
    for case in Case.objects.all():
        case.urn = standardise_urn(case.urn)
        case.save()


class Migration(migrations.Migration):

    dependencies = [
        ('plea', '0021_auto_20151208_1619'),
    ]

    operations = [
        migrations.RunPython(standardise_urns)
    ]
