import json

from django.core.serializers.json import DjangoJSONEncoder


class DateAwareSerializer(object):
    def dumps(self, obj):
        return DjangoJSONEncoder(sort_keys=True).encode(obj).encode()

    def loads(self, data):
        return json.loads(data.decode())
