import json
import datetime
from time import mktime

from django.core.serializers.json import DjangoJSONEncoder


def load_with_datetime(pairs):
    d = {}

    for k, v in pairs:
        if isinstance(v, basestring):
            try:
                d[k] = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                continue
            except ValueError:
                pass

        d[k] = v
    return d


class DateAwareSerializer(object):
    def dumps(self, obj):
        s = json.dumps(obj, cls=DjangoJSONEncoder)
        print s
        return s

    def loads(self, data):
        j = json.loads(data, object_pairs_hook=load_with_datetime)
        print j
        return j