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


class AuditedValidationError(serializers.ValidationError):
    """A subclass of ValidationErrors that also creates audit events"""

    def __init__(self, *args, **kwargs):
        event_data = kwargs.pop("event_data")
        super(AuditedValidationError, self).__init__(*args, **kwargs)
        AuditEvent().populate(**event_data)


class OffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offence
        exclude = ("case",)


class AuditEventSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = AuditEvent
        exclude = ('case', 'event_data')
        required_fields = ("event_type", "event_subtype")

    def post_validate(self):
        if self.errors:
            raise AuditedValidationError(
                "Error validating audit event via API",
                event_data=self.data)


class CaseSerializer(serializers.ModelSerializer):
    # FIXME: using modelserialiser would suggest not defining fields directly:w
    case_number = serializers.CharField(required=True)
    print("case_number1: " + str(case_number))
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format])
    print("urn1: " + str(urn))
    offences = OffenceSerializer(many=True)
    print("offences: " + str(offences))
    ou_code = serializers.CharField(required=True)
    print("ou_code: " + str(ou_code))
    accepted_initiation_types = ['J', 'Q', 'S']

    def __init__(self, *args, **kwargs):
        super(CaseSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = ("offences", "urn", "extra_data", "date_of_hearing",
                  "case_number", "initiation_type", "language", "ou_code")

    def validate(self, data):
        if "date_of_hearing" not in data:
            AuditEvent().populate(
                event_type="case_api",
                event_subtype="invalid_case_missing_dateofhearing",
                event_trace=str(data),
            )
            raise serializers.ValidationError(
                "date_of_hearing is a required field")

        if len(data.get("offences", [])) == 0:
            AuditEvent().populate(
                event_type="case_api",
                event_subtype="case_invalid_no_offences",
                event_trace=str(data),
            )
            raise serializers.ValidationError("case has no offences")

        offence_codes = [
            offence["offence_code"][:4]
            for offence in data["offences"]]

        match = all([
            CaseOffenceFilter.objects.filter(
                filter_match__startswith=offence_code).exists()
            for offence_code in offence_codes])

        if not match:
            AuditEvent().populate(
                event_type="case_api",
                event_subtype="case_invalid_not_in_whitelist",
                event_trace=str(data),
            )
            raise serializers.ValidationError(
                ("Case {} contains offence codes [{}] not present "
                 "in the whitelist").format(
                    data.get("urn"),
                    offence_codes))

        init_type = data.get("initiation_type", "")
        if init_type not in self.accepted_initiation_types:
            AuditEvent().populate(
                event_type="case_api",
                event_subtype="case_invalid_invalid_initiation_type",
                event_trace=str(data),
            )
            raise serializers.ValidationError(
                "Case contains invalid initiation type {}".format(
                    data.get("initiation_type", "")))

        urn = data.pop("urn")
        std_urn = standardise_urn(urn)
        data["urn"] = std_urn

        # Has this URN been used already?
        sent_case = Case.objects.filter(
            urn=std_urn,
            case_number=data["case_number"],
            sent=True).exists()
        print("sent_case: " + str(sent_case))

        if sent_case:
            AuditEvent().populate(
                event_type="case_api",
                event_subtype="case_invalid_duplicate_urn_used",
                event_trace=str(data),
            )
            raise serializers.ValidationError(
                "URN / Case number already exists and has been used")

        return data

    def create(self, validated_data):
        # Create the case instance
        offences = validated_data.pop("offences", [])

        # Update or create?
        open_cases = Case.objects.filter(
            urn=validated_data["urn"],
            case_number=validated_data["case_number"],
            sent=False)
        print("open_cases" + str(open_cases))

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

        AuditEvent().populate(
            event_type="case_api",
            event_subtype="success",
            event_trace=str(case),
            case=case,
        )

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
    print("case_number2: " + str(case_number))
    urn = serializers.CharField(required=True, validators=[is_valid_urn_format, ])
    print("urn2: " + str(urn))

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
        sent_results = Result.objects.filter(
            urn=urn,
            case_number=data["case_number"],
            sent=True).exists()
        print("sent_results" + str(sent_results))

        if sent_results:
            AuditEvent().populate(
                event_type="result_api",
                event_subtype="result_invalid_duplicate_urn_used",
                event_trace="URN: {0}".format(urn),
            )
            raise serializers.ValidationError(
                "URN / Result number already exists and has been used")

        return data

    def create(self, validated_data):
        # Create the case instance
        offences = validated_data.pop("result_offences", [])

        # Update or create?
        open_results = Result.objects.filter(
            urn=validated_data["urn"],
            case_number=validated_data["case_number"],
            sent=False)
        print("open_results" + str(open_results))

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
        fields = '__all__'
