from rest_framework import serializers

from apps.plea.models import Case


def validate_case_number(value):
    """
    Make sure case number is unique
    """

    try:
        Case.objects.get(case_number=value)
    except (Case.DoesNotExist, Case.MultipleObjectsReturned):
        return value
    else:
        raise serializers.ValidationError("Case with this case number already exists")
