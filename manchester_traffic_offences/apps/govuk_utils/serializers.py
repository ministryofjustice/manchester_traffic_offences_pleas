import json

from django.core.serializers.json import DjangoJSONEncoder


class DateAwareSerializer(object):
    def dumps(self, obj):
        return json.dumps(obj, cls=DjangoJSONEncoder)

    def loads(self, data):
        return json.loads(data)
