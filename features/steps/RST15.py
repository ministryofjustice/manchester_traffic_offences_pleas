"""
BDD tests for features in JIRA #RST15

TODO: Move obviously sharable tests into a common module
"""

import os
import json
import base64

import requests
from selenium.common.exceptions import *
from behave import given, when, then


@when(u'an api call is made to create a "{obj}"')
def step_impl(context, obj):

    if obj == "audit event":
        data = [
            item
            for item in context.fixtures["auditevent_create_api"]
            if item["model"] == "plea.auditevent"
        ]
        url = context.TESTING_SERVER_API_URL + "/api/v0/auditevent/"
        method = "post"

    elif obj == "case":
        data = [
            item
            for item in context.fixtures["auditevent_create_api"]
            if item["model"] == "plea.auditevent"
        ]
        method = "post"

    else:
        raise NotImplementedError("Object type not supported")

    context.api_response = getattr(requests, method)(
        url,
        headers=context.api_user["auth_header"],
        data=data,
    )


@when(u'I visit "{location}"')
def step_impl(context, location):
    """Possibly the mose re-uasable step"""
    url = context.TESTING_SERVER_APP_URL + location
    context.response = context.browser.get(url)


@when(u'the "{obj}" is posted to the api')
def step_impl(context, obj):
    """"""
    url = context.TESTING_SERVER_API_URL + "/{}/v0/create".format(
        obj.strip(" "))
    context.api_response = requests.post(
        url,
        headers=context.api_user["auth_header"],
        data={
            "urn": "TODO: kfkjkj"
        })


"""
Steps that test objects
"""


@then(u'the "{obj}" is saved')
def step_impl(context, obj):
    raise NotImplementedError(u'STEP: Then the object is saved')


@then(u'the "{obj}" is not saved')
def step_impl(context, obj):
    raise NotImplementedError(u'STEP: Then the object is not saved')


@then(u'the "{obj}" has a "{field_name}"')
def step_impl(context, obj, field_name):
    raise NotImplementedError(u'STEP: Then the object has a fieldname')


@then(u'the response is "{expected}"')
def step_impl(context, expected):
    if expected == "success":
        if not context.api_response.status_code == 200:
            raise ValueError(
                "API response status_code was wrong, expected 200, got {}".format(
                    context.api_response.status_code))
    elif expected == "failure":
        if context.api_response.status_code == 200:
            raise ValueError("API response was 200")
    else:
        raise NotImplementedError("Don't know how to hande that expectation")


@then(u'the "{obj}" field "{field_name}" has the value "{field_value}"')
def step_impl(context, obj, field_name, field_value):
    raise NotImplementedError(
        u'STEP: Then the object field field_name has the value field_value')


@then(u'the "{obj}" field "{field_name}" is present')
def step_impl(context, obj, field_name):
    raise NotImplementedError(
        u'STEP: Then the object field field_name is present')


@then(u'the "{obj}" field "{field_name}" is not present')
def step_impl(context, obj, field_name):
    raise NotImplementedError(
        u'STEP: Then the object field field_name is not present')


@then(u'I see the related "{obj}" with pk "{pk}"')
def step_impl(context, obj, pk):
    raise NotImplementedError(
        u'STEP: Then I see the related object with pk pk')


"""
Steps to test related objects
"""


@then(u'I see no related "{obj}"')
def step_impl(context, obj):
    raise NotImplementedError(u'STEP: Then I see no related object')


@then(u'I see the details of the "{obj}" with pk "{pk}"')
def step_impl(context, obj, pk):
    raise NotImplementedError(u'STEP: Then I see the details of the ')


@then('I see a list of "{obj}" items')
def step_impl(context, obj):
    items = context.response_as_rows(context)
    if not items:
        raise Exception("No items in list")


@then(u'I see the "{obj}" list sorted by "{key}" in "{order}" order')
def step_impl(context, obj, key, order):
    """Ensure a list is sorted"""

    # TODO: URN will need work to be sortable
    if key.lower() != "urn":

        last_value = ""
        for row in context.response_as_rows(context):
            this_value = getattr(row, key.lower().encode("utf-8"))
            error = False
            if order == "ascending":
                if this_value <= last_value:
                    error = True
            elif order == "descending":
                if this_value >= last_value:
                    error = True
                raise ValueError(
                    "row {0} is not sorted by {1}, scenario status is {2}, {3}".format(
                        row.id, key.lower(), context.scenario.status, (
                            row, key.lower(),
                            last_value,
                            [getattr(row, att) for att in dir(row) if not att.startswith("_")])))
            last_value = getattr(row, key.lower().encode("utf-8"))


@then(u'I see the "{obj}" list filtered by "{key}" = "{value}"')
def step_impl(context, obj, key, value):

    # TODO: consider the business rules for filtering on urn when urn exists in
    # both the case and extra_data
    if not(key.lower() == "urn" and value == "123"):
        for row in context.response_as_rows(context):
            if getattr(row, key.lower()) != value:
                raise ValueError(
                    "row {0} is not filtered by {1}".format(row.id, key))


@then(u'the "{obj}" stack trace is present')
def step_impl(context, obj):
    raise NotImplementedError(
        u'STEP: Then the object stack trace is present')


@then(u'I see "{msg}" in the page')
def step_impl(context, msg):
    assert msg in context.browser.find_elements_by_tag_name(
        "html")[0].get_attribute('innerHTML')


@then(u'I see the admin interface for "{obj}"')
def step_impl(context, obj):
    expected = "Select {} to change | Django site admin".format(obj.lower())
    actual = context.browser.title
    if actual != expected:
        raise ValueError(
            "Title error, expected {0}, got {1}".format(
                expected,
                actual))


@then(u'the "{obj}" contains a hash of the details of the case')
def step_impl(context, obj):
    raise NotImplementedError(
        u'STEP: Then the object contains a hash of the details of the case')


@then(u'I see pleas grouped by court centre')
def step_impl(context):
    context.scenario.skip()


@then(u'I see stats grouped into 4 week entries')
def step_impl(context):
    context.scenario.skip()


@then(u'I see a link to the weekly stats')
def step_impl(context):
    context.scenario.skip()


@then(u'I see a link to the monthly stats')
def step_impl(context):
    context.scenario.skip()


@then(u'I see the "{model_name}" with pk "{pk}" from "{fixture_file}"')
def step_impl(context, model_name, fixture_file, pk):
    """
    Compare the details seen in the admin with the fixture that was presented
    TODO: generalise this for any key/value
    """
    expected = context.get_fixtures(
        context,
        fixture_file,
        model_name,
        pk=pk,
    )[0]
    actual = context.response_as_item(context)

    for k in expected["fields"]:
        actual_field_name = getattr(actual["fields"], k)
        if k != actual_field_name:
            raise ValueError(
                "object {0} {1} mismatch, {2} != {3}".format(
                    model_name,
                    pk,
                    model_name[k],
                    actual_field_name,
                )
            )


@when(u'I visit the "{obj}" with pk "{pk}"')
def step_impl(context, obj, pk):
    url = context.TESTING_SERVER_APP_URL + "/admin/plea/{0}/{1}/".format(
        obj.strip(" "),
        pk,
    )
    context.browser.get(url)


def complete_plea(context, case):
    """Drive the browser to submit a plea"""
    return "something"


@when('I complete all outstanding user plea journies')
def step_impl(context):
    context.responses = []
    for item in context.fixtures["sanitised_prod_data"]:
        if item["model"] == "plea.case":
            context.responses.append(
                complete_plea(context, item["pk"]))


@then('I see "{msg}" at the end of each journey')
def step_impl(context, msg):
    for response in context.responses:
        assert msg in response.data
