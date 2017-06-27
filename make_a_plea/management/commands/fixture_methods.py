import datetime
import os
import json

from apps.plea.models import AuditEvent, Case, Court, Offence


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type %s not serializable" % type(obj))


class FixtureLoader(object):
    """Methods specific to loading fixtures directly"""

    def get_creation_order(self, data):
        """
        Based on the data given, determine foreign key constraints and
        return list of keys in the order to create the corresponding objects.

        When fixtures become more complex, change weighting and ordering to
        use toposort or similar.
        """

        # Discover foreign key vectors
        vectors = []  # array of tuples of keys (from, to)
        for lkey in data:
            for rkey in data:

                fk_patterns = [  # There are inconsistencies in our architecture
                    rkey,
                    "{}id".format(rkey),
                    "{}_id".format(rkey),
                ]
                for pattern in fk_patterns:
                    if all([
                        any([
                            pattern in obj.keys()
                            for obj in data[lkey]
                        ]),
                        (lkey, rkey) not in vectors
                    ]):
                        vectors.append((lkey, rkey))

        if self.options["verbose"]:
            print vectors

        # Determine weighting by appearance in vectors
        unordered_keys = {}
        for lkey, rkey in vectors:
            if rkey not in unordered_keys:
                unordered_keys[rkey] = 1
            else:
                unordered_keys[rkey] += 1
            if lkey not in unordered_keys:
                unordered_keys[lkey] = 1 + len(vectors)
            else:
                unordered_keys[lkey] += 1 + len(vectors)
        for key in data:
            if key not in unordered_keys:
                unordered_keys[key] = 0

        ordered_keys = [
            k
            for k, _ in sorted(
                unordered_keys.iteritems(),
                key=lambda (k, v): (v, k))
        ]

        if self.options["verbose"]:
            print ordered_keys

        return ordered_keys

    def load(self):
        """Loads data directly, by batch"""

        modelmap = {
            "case": Case,
            "auditevent": AuditEvent,
            "offence": Offence,
            "court": Court,
        }

        for batch in self.yield_batches():
            self.process(batch, modelmap)
            for item_type, items in batch.items():
                self.pk_offsets[item_type] += len(items)


class FixtureGenerator(object):
    """Methods relating to generating fixture files in django fixture format"""

    def batch_to_django_fixtures(self, batch, modelmap):
        """Generate a list of ojects in django fixture format from a batch"""

        retval = []
        for model in batch:  # A batch may contain various different models
            for itemtype, itemlist in batch.items():
                for item in itemlist:
                    item["pk"] = self.pk_offsets[itemtype]
                    retval.append(
                        {
                            "model": modelmap[itemtype],
                            "pk": item["pk"],
                            "fields": {
                                k: v
                                for k, v in item.items()
                                if k not in ["id", "pk"]
                            },
                        }
                    )
                    self.pk_offsets[itemtype] += 1
        return retval

    def generate(self):
        """Generate fixture files from data"""
        modelmap = {
            "case": "plea.case",
            "auditevent": "plea.auditevent",
            "offence": "plea.offence",
            "court": "plea.court",
        }

        with open(
            os.path.join(
                ROOT_DIR,
                "cucumber",
                "features",
                "{}.json".format(self.category.__name__),
            ),
            "w"
        ) as fixture_file:

            fixture_file.write("[")
            snippets = []
            for batch in self.yield_batches():
                for item in self.process(
                    self.batch_to_django_fixtures(batch, modelmap),
                    modelmap,
                ):
                    snippets.append(
                        json.dumps(
                            item,
                            indent=4,
                            default=json_serial))
            fixture_file.write(",".join(snippets))
            fixture_file.write("]")


class FixtureMethods(FixtureLoader, FixtureGenerator):
    METHOD_ARGS = ["load", "generate"]

    def init_method(self):
        self.method = getattr(self, self.options["method"])

    def process(self, data, mapping):
        """
        Given some related data representing objects, apply the constructor
        to the objects, maintaining referential integrity.

        For the load method mapping values should be classes of the to create the
        objects and uses real ids.

        In the case where the mapping objects are strings, create consistent pks
        for objects with the scope of all batches.

        :param data: The data to be constructed
        :type data: dict whose keys are the mapping keys and values are arrays
        of the attribute values of the objects to process
        :param mapping: Constructor hints
        :type mapping: dict whose keys are the data keys and the values are
        classes or strings
        :return: list of dictionaries in django fixture format or None
        :rtype: list or None
        """
        if self.method == self.generate:
            if self.options["verbose"]:
                print "Generating fixtures..."

            retval = []
            for item in data:
                retval.append({
                    "model": mapping[key],
                    "pk": item["id"],
                    "fields": {
                        k: v
                        for k, v in item.items()
                        if k != "id"
                    }
                })
            return retval

        elif self.method == self.load:
            if self.options["verbose"]:
                print "Loading fixtures..."

            for key in self.get_creation_order(data):
                for item in data[key]:

                    if "id" in item:
                        id_ = item["id"]
                        del item["id"]

                    if mapping[key] == Case:
                        pass
                    if mapping[key] == AuditEvent:
                        if item["case"]:  # Find the actual case (already loaded)
                            related_case_id = [
                                c
                                for c in data["case"]
                                if c["id"] == item["case"]
                            ][0]["pk"]
                            item["case"] = Case.objects.get(pk=related_case_id)
                    if mapping[key] == Offence:
                        if item["case_id"]:  # Find the actual case (already loaded)
                            related_case_id = [
                                c
                                for c in data["case"]
                                if c["id"] == item["case_id"]
                            ][0]["pk"]
                            item["case_id"] = related_case_id  #Case.objects.get(pk=related_case_id)
                    if mapping[key] == Court:
                        pass
                    print item
                    obj = mapping[key](**item)
                    obj.save()
                    item["pk"] = obj.id

                    try:  # Put the id back so that other references to this object may be processed
                        item["id"] = id_
                    except NameError:
                        pass


        else:
            raise NotImplementedError

        if True:
            pass
            """
            for court in batch["courts"]:
                court_obj = Court(**{
                    k: v
                    for k, v in court.items()
                    if k not in ["id", "pk"]
                }) if "pk" not in court else None
                if court_obj:
                    court_obj.save()
                    court["pk"] = court_obj.id

            for case in batch["cases"]:
                case_obj = Case(**{
                    k: v
                    for k, v in case.items()
                    if k not in ["id", "pk"]
                }) if "pk" not in case else None
                if case_obj:
                    case_obj.save()
                    case["pk"] = case_obj.id

            for offence in batch["offences"]:
                offence_obj = Offence(**{
                    k: v
                    for k, v in offence.items()
                    if k not in ["id", "pk"]
                }) if "pk" not in offence else None
                if offence_obj:
                    if "caseid" in offence:
                        offence_obj.case = Case.objects.get(
                            pk=[
                                case["pk"]
                                for case in batch["cases"]
                                if case["id"] == offence["caseid"] + self.PK
                            ][0])
                    offence_obj.save()
                    offence["pk"] = offence_obj.id

            for auditevent in batch["auditevents"]:
                auditevent_obj = AuditEvent().populate(**{
                    k: v
                    for k, v in auditevent.items()
                    if k not in ["id", "pk", "case"]
                }) if "pk" not in auditevent else None
                if auditevent_obj:
                    if "caseid" in auditevent:
                        auditevent_obj.case = Case.objects.get(
                            pk=[
                                case["pk"]
                                for case in batch["cases"]
                                if case["id"] == auditevent["caseid"]
                            ][0])
                    auditevent_obj.save()
                    auditevent["pk"] = auditevent_obj.id
        """
