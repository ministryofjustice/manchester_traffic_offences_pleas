from rest_framework import serializers

from apps.plea.models import Case, UsageStats, Offence


class OffenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offence
        exclude = ("case",)


class CaseSerializer(serializers.ModelSerializer):
    urn = serializers.RegexField("^\d{2}/[a-zA-Z]{2}/\d+/\d{2}$", max_length=16, min_length=14)\

    offences = OffenceSerializer(many=True)

    class Meta:
        model = Case
        fields = ("offences", "urn", "title", "name", "forenames", "surname",
                  "case_number")

    def create(self, validated_data):

        # Create the case instance

        offences = validated_data.pop("offences", [])

        case = Case.objects.create(**validated_data)

        # Create or update each page instance
        for item in offences:
            page = Offence(**item)
            page.case = case
            page.save()

        return case

    def validate(self, attrs):

        if not Case.objects.can_use_urn(attrs["urn"]):

            raise serializers.ValidationError("Case data already exists")

        return attrs


class UsageStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageStats