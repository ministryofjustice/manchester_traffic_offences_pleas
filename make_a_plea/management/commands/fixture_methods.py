"""
Fixture Methods
===============

A mixin class for the fixtures command containing the methods of operation.

--method load

Load fixtures directly.

 * Generate a unique, dynamic set of fixtures on an existing environment
 * Quick, no need to move files around

--method generate

Generate Django fixture file.

 * Generate fixtures without needing a running instance
 * File allows identical fixtures to be loaded between environments or after a flush

"""

import datetime
import os
import json

from django.db.utils import IntegrityError

from apps.plea.models import Case, Court


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
    """Mixin with methods specific to loading fixtures directly"""

    def get_dependency_list(self, data):
        """Use topological sorting to determine dependency list of objects"""
        relationships = {}
        for lkey in data:
            relationships[lkey] = []
            for rkey in data:
                rprefix, rmodel = rkey.split(".")
                fk_patterns = [  # There are inconsistencies in our design
                    rmodel,
                    "{}id".format(rmodel),
                    "{}_id".format(rmodel),
                ]
                for pattern in fk_patterns:
                    if all([
                        any([
                            pattern in obj.keys()
                            for obj in data[lkey]
                        ]),
                        rkey not in relationships[lkey]
                    ]):
                        relationships[lkey].append(rkey)
        return [
            (k, v)
            for k, v in relationships.items()
        ]

    def get_creation_order(self, data):
        """
        Based on the data given yield keys in the order to create the corresponding objects.
        Taken from https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list.
        """

        provided = set()
        data = self.get_dependency_list(data)

        while data:
            remaining_items = []
            emitted = False

            for item, dependencies in data:
                if provided.issuperset(dependencies):
                    yield item
                    provided.add(item)
                    emitted = True
                else:
                    remaining_items.append((item, dependencies))

            if not emitted:
                raise Exception("Topological sort failure")

            data = remaining_items

    def load(self):
        """Loads data directly, by batch"""

        for batch in self.yield_batches():
            self.process(batch, self.modelmap)


class FixtureGenerator(object):
    """Mixin with mthods relating to generating fixture files in django fixture format"""

    def generate(self):
        """Generate fixture files from data"""

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
                for item in self.process(batch):
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
        """Initialise method-related concerns."""
        self.method = getattr(self, self.options["method"])

    def get_item_from_data(self, data, model, pk):
        """Find an instance of a model in the data"""
        filtered = []
        for i in data[model]:
            try:
                if i["id"] == pk:
                    filtered.append(i)
            except KeyError as e:
                raise e
        return filtered[0]

    def process(self, data, mapping=None):
        """
        Given some related data representing objects, apply the constructor
        to the objects, maintaining referential integrity of the items.

        For the load method, mapping values should be provided that are classes
        of the objects to create. This method uses real ids.

        For the generate method, a mapping is not required, the model string
        is used directly. PKs are maintained for objects with the scope of all batches.

        The term 'id' refers to the id of objects in the batch being processed and 'pk'
        refers to the django id of installed objects.

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
            if mapping is not None:
                raise Exception("Mapping should not provided to generate method")
            if self.options["verbose"]:
                print "Generating a batch of fixtures..."

            return [
                {
                    "model": model,
                    "pk": item["id"],
                    "fields": {
                        k: v
                        for k, v in item.items()
                        if k not in ["id", "pk"]
                    }
                }
                for model in data
                for item in data[model]
            ]

        elif self.method == self.load:
            if mapping is None:
                raise Exception("Mapping must be provided to load method")
            if self.options["verbose"]:
                print "Loading a batch of fixtures..."

            for model in self.get_creation_order(data):
                for item in data[model]:

                    if "id" in item:
                        id_ = item["id"]
                        del item["id"]

                    # Handle a case
                    if model == "plea.case":
                        pass

                    # Handle a court
                    if model == "plea.court":
                        pass

                    # Handle an audit event
                    if model == "plea.auditevent":
                        if "case" in item:
                            if item["case"]:  # Find the actual case (already loaded)
                                item["case"] = Case.objects.get(
                                    pk=self.get_item_from_data(
                                        data,
                                        "plea.case",
                                        item["case"],
                                    )["pk"]
                                )

                    # Handle an offence
                    if model == "plea.offence":
                        if item["case_id"]:  # Find the case id (already loaded)
                            item["case_id"] = self.get_item_from_data(
                                data,
                                "plea.case",
                                item["case_id"],
                            )["pk"]

                    # Handle an OUCode
                    if model == "plea.oucode":
                        if item["court"]:  # Find the actual court (already loaded)
                            item["court"] = Court.objects.get(
                                pk=self.get_item_from_data(
                                    data,
                                    "plea.court",
                                    item["court"],
                                )["pk"]
                            )

                    # Create the object and update the item's id
                    obj = mapping[model](**item)
                    if model == "auth.user":  # Handle user password hashing
                        obj.set_password(item["password"])
                        try:
                            obj.save()
                        except IntegrityError:
                            pass
                    else:
                        obj.save()

                    item["pk"] = obj.id

                    try:  # Put the id back so that other references to this object may be processed
                        item["id"] = id_
                    except NameError:
                        pass
        else:
            raise NotImplementedError
