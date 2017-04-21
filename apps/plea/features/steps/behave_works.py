import behave
from behave import given, when, then


@given(u'django-behave is installed')
def step_impl(context):
    assert behave


@when(u'the django-behave tests are invoked')
def step_impl(context):
    # We are here
    assert True


@then(u'this test passes')
def step_impl(context):
    # A bit meta
    assert True


@then(u'other tests still run fine')
def step_impl(context):
    # Existing tests are invoked before these tests. If we reach here those tests still run
    assert True

