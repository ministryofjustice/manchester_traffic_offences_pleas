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


@given(u'fixtures from "{file_name}" are loaded')
def step_impl(context, file_name):
    """Load fixtures"""
    context.load_fixtures(file_name)


@given(u'fixtures from "{fixture_file}" are available')
def step_impl(context, fixture_file):
    """
    Ensure the fixture with id is loaded from fixture_file

    These fixtures are not loaded into the database, intead they are held on
    the context to be used during requests

    TODO: re-use the context.load_fixtures method
    """
    project_root = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__))))
    fixture_path = os.path.join(
        project_root,
        "fixtures",
        fixture_file + ".json")

    if fixture_file not in context.fixtures:
        with open(fixture_path, "r") as f:
            context.fixtures[fixture_file] = json.loads(f.read())
