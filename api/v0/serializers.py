import datetime as dt

from rest_framework import serializers

from apps.plea.models import Case


class CaseSerializer(serializers.ModelSerializer):
    urn = serializers.RegexField("^\d{2}/[a-zA-Z]{2}/\d+/\d{2}$", max_length=16, min_length=14)

    class Meta:
        model = Case
        fields = ('urn', 'hearing_date', 'name')

    def validate(self, attrs):
        if not Case.objects.is_unique(attrs['urn'],
                                      attrs['hearing_date'],
                                      attrs['name']):

            raise serializers.ValidationError("Case data already exists")

        return attrs