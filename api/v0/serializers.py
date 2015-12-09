import json

from django.core import exceptions
from rest_framework import serializers

from apps.plea.models import Case, UsageStats, Offence, Result, ResultOffence, ResultOffenceData
from apps.plea.standardisers import standardise_urn
from apps.plea.validators import is_valid_urn_format

from api.validators import validate_case_number


class OffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offence
        exclude = ("case",)


class CaseSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(required=True)
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format, ])
    offences = OffenceSerializer(many=True)

    def __init__(self, *args, **kwargs):
        super(CaseSerializer, self).__init__(*args, **kwargs)

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

        # Has this URN been used already?
        sent_case = Case.objects.filter(urn=urn,
                                        case_number=validated_data["case_number"],
                                        sent=True).exists()

        if sent_case:
            raise exceptions.ValidationError("URN / Case number already exists and has been used")

        # Update or create?
        open_cases = Case.objects.filter(urn=urn,
                                         case_number=validated_data["case_number"],
                                         sent=False)

        if open_cases:
            case = open_cases[0]
            case.offences.all().delete()
            case.initiation_type = validated_data["initiation_type"]
            case.language = validated_data["initiation_type"]
            case.extra_data = validated_data["extra_data"]
            case.save()
        else:
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
        fields = ("result_code", "result_short_title", "result_short_title_welsh",
                  "result_wording",
                  "result_wording_welsh")


class ResultOffenceSerializer(serializers.ModelSerializer):
    offence_data = ResultOffenceDataSerializer(many=True)

    class Meta:
        model = ResultOffence
        fields = ("offence_data", "offence_code", "offence_seq_number")


class ResultSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(required=True, validators=[validate_case_number, ])
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format, ])

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

        # Has this URN been used already?
        sent_results = Result.objects.filter(urn=urn,
                                             case_number=validated_data["case_number"],
                                             sent=True).exists()

        if sent_results:
            raise exceptions.ValidationError("URN / Result number already exists and has been used")

        # Update or create?
        open_results = Result.objects.filter(urn=urn,
                                             case_number=validated_data["case_number"],
                                             sent=False)

        if open_results:
            result = open_results[0]
            result.result_offences.all().delete()
            result.account_number = validated_data["account_number"]
            result.division = validated_data["division"]
            result.instalment_amount = validated_data["instalment_amount"]
            result.lump_sum_amount = validated_data["lump_sum_amount"]
            result.pay_by_date = validated_data["pay_by_date"]
            result.payment_type = validated_data["payment_type"]
            result.save()
        else:
            result = Result.objects.create(**validated_data)

        for item in offences:
            data = item.pop("offence_data")
            offence = ResultOffence(**item)
            offence.result = result
            offence.save()

            for offence_data in data:
                offence.offence_data.create(**offence_data)

        return result


class UsageStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageStats