from rest_framework import serializers

from apps.plea.models import Case, UsageStats


class CaseSerializer(serializers.ModelSerializer):
    urn = serializers.RegexField("^\d{2}/[a-zA-Z]{2}/\d+/\d{2}$", max_length=16, min_length=14)

    class Meta:
        model = Case
        fields = ('urn',)

    def validate(self, attrs):
        if not Case.objects.can_use_urn(attrs['urn']):

            raise serializers.ValidationError("Case data already exists")

        return attrs


class UsageStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageStats