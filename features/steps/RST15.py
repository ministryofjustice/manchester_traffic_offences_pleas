"""
BDD tests for features in JIRA #RST15

TODO: Move obviously sharable tests into a common module
"""

import os
import json

from selenium.common.exceptions import *
from behave import given, when, then


@given(u'I am logged into the admin interface as "{first_name}"')
def step_impl(context, first_name):
    """Log in as the user with the given first_name"""

    # Make sure we're logged out
    i_am_logged_out_of_the_admin_interface(context)

    # Log in as the user
    user = context.get_fixtures(
        context,
        "default",
        "auth.user",
        first_name=first_name,
    )[0]

    # TODO: fix up passwords after load so this hack isn't required and
    # fixtures can contain clear passwords
    user["password"] = user["username"]

    try:
        username_element = context.browser.find_element_by_id("id_username")
        password_element = context.browser.find_element_by_id("id_password")
        submit_element = context.browser.find_element_by_xpath("//input[@type='submit']")
    except NoSuchElementException:
        context.check_axes(context)
    else:
        username_element.send_keys(user["username"])
        password_element.send_keys(user["password"])
        submit_element.click()

    # Confirm the correct user is logged in
    try:
        logged_in_name = context.browser.find_element_by_id(
            "user-tools").find_elements_by_tag_name(
                "strong")[0].get_attribute('innerHTML')
    except NoSuchElementException:
        context.check_axes(context)
    else:
        if logged_in_name != user["first_name"]:
            raise ValueError(
                "Logged in username was not {0}, got {1} instead".format(
                    first_name, logged_in_name))


@given(u'I am logged out of the admin interface')
def i_am_logged_out_of_the_admin_interface(context):
    """
    Supports:

        * Django admin interface
    """

    # Logout
    url = context.TESTING_SERVER_APP_URL + "/admin/logout/"
    context.browser.get(url)

    # Confirm logout
    try:
        context.browser.find_element_by_id("id_username")
        context.browser.find_element_by_id("id_password")
        context.browser.find_element_by_xpath("//input[@type='submit']")
    except NoSuchElementException:
        context.check_axes(context)


@given(u'fixtures from "{file_name}" are loaded')
def step_impl(context, file_name):
    """Load fixtures"""
    context.load_fixtures(file_name)


@when(u'an api call is made to create a "{obj}"')
def step_impl(context, obj):
    raise NotImplementedError(
        u'STEP: When an api call is made to create an audit event')


@when(u'I visit "{location}"')
def step_impl(context, location):
    """Possibly the mose re-uasable step"""
    url = context.TESTING_SERVER_APP_URL + location
    context.response = context.browser.get(url)


"""
Steps that test the API

# BDD tests that use the API should not short-circuit the external interface of
# the system. Do not directly manipulate model objects or use APIClient. Tests
# that do that belong in the api tests.
"""


@given(u'I am logged into the api interface as "{first_name}"')
def step_impl(context, first_name):
    """
    TBD
    """
    import requests

    user_fixture = context.get_fixtures(
        context,
        "default",
        "auth.user",
        first_name=first_name,
    )[0]

    context.api_client.login(
        user_fixture["username"],
        user_fixture["password"],
    )


@when(u'the "{obj}" is posted to the api')
def step_impl(context, obj):
    """"""
    url = context.TESTING_SERVER_API_URL + "/{}/v0/create".format(
        obj.strip(" "))
    context.api_client.post(
        url,
        {
            "urn": "TODO: kfkjkj"
        })
    raise NotImplementedError(u'STEP: When the object is posted to the api')


"""
Steps that tests objects
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


@then(u'the response is "{response}"')
def step_impl(context, response):
    raise NotImplementedError(u'STEP: Then the response is response')


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


@then(u'I see the "{obj}" list sorted by "{key}"')
def step_impl(context, obj, key):
    """Ensure a list is sorted"""
    last_value = ""
    for row in context.response_as_rows(context):
        if getattr(row, key) < last_value:
            raise ValueError(
                "row {0} is not filtered by {1}").format(row.row_id, key)
        last_value = getattr(row, key)


@then(u'I see the "{obj}" list filtered by "{key}" = "{value}"')
def step_impl(context, obj, key, value):
    for row in context.response_as_rows(context):
        if getattr(row, key) != value:
            raise ValueError(
                "row {0} is not filtered by {1}").format(i, key)


@then(u'the "{obj}" stack trace is present')
def step_impl(contexti, obj):
    raise NotImplementedError(
        u'STEP: Then the object stack trace is present')


@then(u'I see the admin interface for "{obj}"')
def step_impl(context, obj):
    expected = "Select {} to change".format(obj.strip(" ").lower())
    if not context.browser.title.startswith(expected):
        raise ValueError(
            "Title was not as expected, got {}".format(
                context.browser.title))


@then(u'I see the admin login form')
def step_impl(context):
    if context.browser.title != "Log in | Django site admin":
        raise ValueError(
            "Title was not as expected, got {}".format(
                context.browser.title))


@then(u'I see the admin logout form')
def step_impl(context):
    if context.browser.title != "Logged out | Django site admin":
        raise ValueError(
            "Title was not as expected, got {}".format(
                context.browser.title))


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


@given(u'fixtures from "{fixture_file}" are available')
def step_impl(context, fixture_file):
    """
    Ensure the fixture with id is loaded from fixture_file

    These fixtures are not loaded into the database, intead they are held on
    the context to be used during requests

    TODO: re-use the context.load_fixtures method
    """
    if fixture_file not in context.fixtures:
        context.fixtures[fixture_file] = json.loads(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(__file__))),
                "fixtures",
                fixture_file + ".json"
            )
        )


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


@then('I see a list of "{obj}" items')
def step_impl(context, obj):
    items = context.response_as_rows(context)
    if not items:
        raise Exception("No items in list")


