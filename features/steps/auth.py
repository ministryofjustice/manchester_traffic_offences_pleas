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


@given(u'I am logged into the admin interface as "{first_name}"')
def step_impl(context, first_name):
    """Log in as the user with the given first_name"""

    # Make sure we're logged out
    i_am_logged_out_of_the_admin_interface(context)

    # Log in as the user
    user = context.get_fixtures(
        context,
        "bdd_auth",
        "auth.user",
        first_name=first_name,
    )[0]

    # TODO: fix up passwords after load so this hack isn't required and
    # fixtures can contain clear passwords
    user["password"] = user["username"]

    # visit the login page
    context.browser.get(
        context.TESTING_SERVER_APP_URL + "/admin/login")

    # Fill out the lgin form
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
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(context.browser, 10)
    wait.until(
        lambda driver: driver.find_element_by_id(
            "user-tools").find_elements_by_tag_name("strong")[0].text)

    logged_in_name = context.browser.find_element_by_id(
        "user-tools").find_elements_by_tag_name(
            "strong")[0].get_attribute('innerHTML')
    #except NoSuchElementException:
    #    context.check_axes(context)
    #else:
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


@given(u'I am logged into the api interface as "{first_name}"')
def step_impl(context, first_name):
    """
    TBD
    """
    import requests

    user = context.get_fixtures(
        context,
        "bdd_auth",
        "auth.user",
        first_name=first_name,
        )[0]

    # TODO: Fix password hashing
    user["password"] = user["username"]
    user["credentials"] = base64.b64encode('{}:{}'.format(
        user["username"], user["password"]))
    user["auth_header"] = {'HTTP_AUTHORIZATION': 'Basic {}'.format(user["credentials"])}
    context.api_user = user


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
