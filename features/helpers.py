import os
import re
from subprocess import Popen, call


def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)


def rreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
    """
    return re.sub('%s$' % pattern, sub, string)


def check_axes(context):
    """
    Maybe AXES kicked in; give a useful error
    TODO: re-raise other exceptions, maybe have a step decorator
    """
    if context.browser.find_elements_by_tag_name(
        "body")[0].get_attribute("innerHTML").startswith(
            "Account locked"):
        raise Exception(
            "AXES lockout. Not a superuser?")


def load_fixtures(fixture_file):
    """
    Helper to load fixtures from file
    TODO: move the base path join here
    """
    call(
        [
            "python",
            "manage.py",
            "loaddata",
            "--settings",
            "make_a_plea.settings.bdd",
            fixture_file,
        ],
        env=os.environ.copy(),
    )


def response_as_item(context):
    """
    Convert admin change page into object

    Supports:

         * Django admin interface
    """

    class Item(object):
        def __init__(self, *args, **kwargs):
            for tag in args:
                setattr(
                    self,
                    tag.id.lreplace("id_", ""),
                    tag.value
                )

    form = context.browser.find_elements_by_tag_name("form")[0]
    item = Item(*[
        tag
        for tag in form
        if tag.id.startswith("id_")
    ])


def response_as_rows(context):
    """
    Convert main tables in html responses to python lists of objects

    Supports:

        * Django admin interface
    """

    class Row(object):
        """Represent a row in a table"""

        def __init__(self, headers, data, *args, **kwargs):
            for th, td in zip(headers, data):
                # Columns named after fields start 'column-'
                matching_classes = [
                    i
                    for i in th.get_attribute("class").split(" ")
                    if i.startswith("column-")
                ]
                if matching_classes:  
                    class_string = matching_classes[0]
                    key = lreplace("column-", "", class_string).lower()
                    value = td.text
                elif th.get_attribute("class").split(" ")[0] == u"action-checkbox-column":
                    # First col is special
                    key = "id"
                    value = int(
                        td.find_elements_by_tag_name("input")[0].get_attribute('value'))
                else:
                    raise ValueError(
                        "Invalid element, {0}, {1}".format(
                            td.tag_name,
                            th.tag_name))
                setattr(self, key, value)

    table = context.browser.find_element_by_id("result_list")
    table_head_items = [
        item
        for item in table.find_elements_by_tag_name(
            "thead")[0].find_elements_by_tag_name("th")
    ]
    tbody = table.find_elements_by_tag_name("tbody")[0]
    table_rows = tbody.find_elements_by_tag_name("tr")

    response = []
    for tr in table_rows:
        table_data = tr.find_elements_by_tag_name("td") + \
            tr.find_elements_by_tag_name("th")
        if not len(table_head_items) == len(table_data):
            raise ValueError(
                "Header and row were different lengths: {0} and {1}".format(
                    len(table_head_items),
                    len(table_data)))
        response.append(Row(table_head_items, table_data))
    return response


def get_fixtures(context, namespace, obj, **kwargs):
    """
    Return matching fixtures from the loaded fixtures by key/value pairs

    TODO: recursive attribute notation? probably not.
    TODO: merge with load_fixtures
    """
    fixtures = []
    for item in context.fixtures[namespace]:
        for k, v in kwargs.items():
            if item["model"] == obj:
                if item["fields"][k] == v:
                    fixture = item["fields"]
                    fixture.update({"pk": item["pk"]})
                    fixtures.append(fixture)
    return fixtures

    """ TODO: this is a more scalable approach, fix it
    return next(
        (
            item
            for item in context.fixtures[namespace]
            for key, value in kwargs.items()
            if item["model"] == "plea.{}".format(obj) and item["fields"][key] == value 
        ),
        None
    )
    """
