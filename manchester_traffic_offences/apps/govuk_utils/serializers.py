import json
import datetime
from time import mktime


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


class DateAwareEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return "{0:%Y-%m-%d}".format(obj)

        return json.JSONEncoder.default(self, obj)


class DateAwareSerializer(object):
    def dumps(self, obj):
        return json.dumps(obj, cls=DateAwareEncoder)

    def loads(self, data):
        return json.loads(data, object_pairs_hook=load_with_datetime)