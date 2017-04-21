import json

from django.core import exceptions
from rest_framework import serializers

from apps.plea.models import (
    AuditEvent,
    Case,
    CaseOffenceFilter,
    Offence,
    UsageStats,
)
from apps.result.models import Result, ResultOffence, ResultOffenceData
from apps.plea.standardisers import standardise_urn
from apps.plea.validators import is_valid_urn_format


class OffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offence
        exclude = ("case",)


class AuditEventSerializer(serializers.ModelSerializer):
    event_subtype = serializers.CharField(required=True)
    event_data = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(AuditEventSerializer, self).__init__(*args, **kwargs)
        self.event_type = 3

    class Meta:
        model = AuditEvent
        exclude = ("case", "event_datetime", "event_type")

    def create(self, validated_data):
        item = AuditEvent(validated_data)
        item.create(validated_data)

    def validate(self, data):
        if "event_subtype" not in data or data["event_subtype" == ""]:
            raise exceptions.ValidationError(
                "Parameter event_subtype must be supplied")

        return data


class CaseSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(required=True)
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format, ])
    offences = OffenceSerializer(many=True)
    ou_code = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(CaseSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = ("offences", "urn", "extra_data", "date_of_hearing",
                  "case_number", "initiation_type", "language", "ou_code")

    def validate(self, data):
        if "date_of_hearing" not in data:
            raise exceptions.ValidationError("date_of_hearing is a required field")

        if len(data.get("offences", [])) == 0:
            raise exceptions.ValidationError("case has no offences")

        offence_codes = [offence["offence_code"][:4] for offence in data["offences"]]
        match = False
        for offence_code in offence_codes:
            if CaseOffenceFilter.objects.filter(filter_match__startswith=offence_code).exists():
                match = True
            else:
                match = False
                break

        if not match:
            raise exceptions.ValidationError("Case {} contains offence codes [{}] not present in the whitelist".format(data.get("urn"),
                                                                                                                       offence_codes))

        urn = data.pop("urn")
        std_urn = standardise_urn(urn)
        data["urn"] = std_urn

        # Has this URN been used already?
        sent_case = Case.objects.filter(urn=std_urn,
                                        case_number=data["case_number"],
                                        sent=True).exists()

        if sent_case:
            raise exceptions.ValidationError("URN / Case number already exists and has been used")

        return data

    def create(self, validated_data):
        # Create the case instance
        offences = validated_data.pop("offences", [])

        # Update or create?
        open_cases = Case.objects.filter(urn=validated_data["urn"],
                                         case_number=validated_data["case_number"],
                                         sent=False)

        if open_cases:
            case = open_cases[0]
            case.offences.all().delete()
            if "ou_code" in validated_data:
                case.ou_code = validated_data["ou_code"]
            if "initiation_type" in validated_data:
                case.initiation_type = validated_data["initiation_type"]
            if "language" in validated_data:
                case.language = validated_data["language"]
            case.extra_data = validated_data["extra_data"]
            case.save()
        else:
            validated_data["imported"] = True
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
    case_number = serializers.CharField(required=True)
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format, ])

    result_offences = ResultOffenceSerializer(many=True)

    class Meta:
        model = Result
        fields = ("result_offences", "urn", "case_number", "ou_code",
                  "date_of_hearing", "account_number", "division",
                  "instalment_amount", "lump_sum_amount", "pay_by_date",
                  "payment_type")

    def validate(self, data):
        urn = data.pop("urn")
        std_urn = standardise_urn(urn)
        data["urn"] = std_urn

        # Has this URN been used already?
        sent_results = Result.objects.filter(urn=urn,
                                             case_number=data["case_number"],
                                             sent=True).exists()

        if sent_results:
            raise exceptions.ValidationError("URN / Result number already exists and has been used")

        return data

    def create(self, validated_data):
        # Create the case instance
        offences = validated_data.pop("result_offences", [])

        # Update or create?
        open_results = Result.objects.filter(urn=validated_data["urn"],
                                             case_number=validated_data["case_number"],
                                             sent=False)

        if open_results:
            result = open_results[0]
            result.result_offences.all().delete()
            if "account_number" in validated_data:
                result.account_number = validated_data["account_number"]
            if "division" in validated_data:
                result.division = validated_data["division"]
            if "instalment_amount" in validated_data:
                result.instalment_amount = validated_data["instalment_amount"]
            if "lump_sum_amount" in validated_data:
                result.lump_sum_amount = validated_data["lump_sum_amount"]
            if "pay_by_date" in validated_data:
                result.pay_by_date = validated_data["pay_by_date"]
            if "payment_type" in validated_data:
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
