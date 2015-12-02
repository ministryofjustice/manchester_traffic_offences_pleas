import json

from rest_framework import serializers

from apps.plea.models import Case, UsageStats, Offence, Result, ResultOffence, ResultOffenceData
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
        fields = ("offences", "urn", "extra_data",
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


class ResultOffenceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultOffenceData


class ResultOffenceSerializer(serializers.ModelSerializer):
    offence_data = ResultOffenceDataSerializer(many=True)

    class Meta:
        model = ResultOffence
        fields = ("offence_data", "offence_code", "offence_seq_number")

    def create(self, validated_data):

        # Create the case instance
        offence_data = validated_data.pop("offence_data", [])

        case = ResultOffence.objects.create(**validated_data)

        # Create or update each page instance
        for item in offence_data:
            data = ResultOffenceData(**item)
            data.result_offence = case
            data.save()

        return case


class ResultSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(required=True, validators=[validate_case_number, ])
    urn = serializers.CharField(required=True, validators=[is_urn_valid, ])

    result_offences = ResultOffenceSerializer(many=True)

    class Meta:
        model = Result
        fields = ("result_offences", "urn", "case_number", "ou_code",
                  "date_of_hearing", "account_number", "division",
                  "instalment_amount", "lump_sum_amount", "pay_by_date",
                  "payment_type")

    def create(self, validated_data):
        # Create the case instance
        offences = validated_data.pop("result_offences", [])

        urn = validated_data.pop("urn")
        std_urn = standardise_urn(urn)

        validated_data["urn"] = std_urn

        result = Result.objects.create(**validated_data)

        # Create or update each page instance
        for item in offences:
            data = item.pop("offence_data")
            offence = ResultOffence(**item)
            offence.result = result
            for offence_data in data:
                offence.offence_data.create(**offence_data)

            offence.save()

        return result


class UsageStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageStats