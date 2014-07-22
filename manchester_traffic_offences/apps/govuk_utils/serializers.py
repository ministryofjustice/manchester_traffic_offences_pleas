import json
from dateutil import parser

from django.core.serializers.json import DjangoJSONEncoder


def load_with_datetime(pairs):
    d = {}

    for k, v in pairs:
        if isinstance(v, basestring) and len(v.strip()) >= 10:
            try:
                d[k] = parser.parse(v, fuzzy=False)
                continue
            except TypeError:
                pass

        d[k] = v
    return d


class DateAwareSerializer(object):
    def dumps(self, obj):
        return json.dumps(obj, cls=DjangoJSONEncoder)

    def loads(self, data):
        return json.loads(data, object_pairs_hook=load_with_datetime)
