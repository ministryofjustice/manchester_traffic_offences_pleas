from behave import given, when, then
from selenium import webdriver


def before_all(context):
    context.browser = webdriver.Firefox()


def after_all(context):
    context.browser.quit()


@when(u'I visit "{url}"')
def step_impl(context, url):
        raise NotImplementedError(u'STEP: When I visit url')


@given(u'the "{obj}" from file "{file_name}"')
def step_impl(context, obj, file_name):
        raise NotImplementedError(
            u'STEP: Given the object from file file_name')


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
        raise NotImplementedError(u'STEP: Then the object field field_name has the value field_value')


@then(u'the "{obj}" field "{field_name}" is present') 
def step_impl(context, obj, field_name):
        raise NotImplementedError(u'STEP: Then the object field field_name is present')


@then(u'the "{obj}" field "{field_name}" is not present') 
def step_impl(context, obj, field_name):
        raise NotImplementedError(u'STEP: Then the object field field_name is not present')


@when(u'the "{obj}" is posted to the api')
def step_impl(context, obj):
        raise NotImplementedError(u'STEP: When the object is posted to the api')


@then(u'I see the related "{obj}" with pk "{pk}"')
def step_impl(context, obj, pk):
        raise NotImplementedError(u'STEP: Then I see the related object with pk pk')


@then(u'I see no related "{obj}"')
def step_impl(context, obj):
        raise NotImplementedError(u'STEP: Then I see no related object')


@then(u'I see the details of the "{obj}" with pk "{pk}"')
def step_impl(context, obj, pk):
        raise NotImplementedError(u'STEP: Then I see the details of the ')


@then(u'I see the "{obj}" sorted by "{key}"')
def step_impl(context, obj, key):
        raise NotImplementedError(u'STEP: Then I see the objects sorted by key')


@given(u'I am logged into the admin interface as "{username}"')
def step_impl(context, username):
        raise NotImplementedError(u'STEP: Given I am logged into the admin interface as username')


@then(u'the "{obj}" stack trace is present')
def step_impl(contexti, obj):
        raise NotImplementedError(u'STEP: Then the object stack trace is present')


@given(u'I am logged out of the admin interface')
def step_impl(context):
        raise NotImplementedError(u'STEP: Given I am logged out of the admin interface')


@then(u'I see the admin interface for "{obj}"')
def step_impl(context, obj):
        raise NotImplementedError(u'STEP: Then I see the admin interface for object') 


@then(u'I see the admin login form')
def step_impl(context):
        raise NotImplementedError(u'STEP: Then I see the admin login form')


@then(u'the "{object}" contains a hash of the details of the case')
def step_impl(context, obj):
    raise NotImplementedError(u'STEP: Then the object contains a hash of the details of the case')


