from rest_framework import serializers

from apps.plea.models import Case, UsageStats, Offence
from apps.plea.standardisers import standardise_urn
from apps.plea.validators import is_urn_valid

from api.validators import validate_case_number


class OffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offence
        exclude = ("case",)


class CaseSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(required=True, validators=[validate_case_number, ])
    urn = serializers.CharField(required=True, validators=[is_urn_valid, ])

    offences = OffenceSerializer(many=True)

    class Meta:
        model = Case
        fields = ("offences", "urn", "title", "name", "forenames", "surname",
                  "case_number", "initiation_type", "language")

    def create(self, validated_data):

        # Create the case instance
        offences = validated_data.pop("offences", [])

        urn = validated_data.pop("urn")
        std_urn = standardise_urn(urn)

        validated_data["urn"] = std_urn

        case = Case.objects.create(**validated_data)

        # Create or update each page instance
        for item in offences:
            offence = Offence(**item)
            offence.case = case
            offence.save()

        return case


class UsageStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageStats