from behave import when
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@given(u'I have validated a personal URN')
def step_impl(context):
    context.execute_steps(u'''
        When I visit "plea/enter_urn/"
        And I submit a valid URN
        And I fill in "number_of_charges" with "2"
        And I fill in correct date of birth
        And I press "Continue"
    ''')

@given(u'I have validated a personal welsh URN')
def step_impl(context):
    context.execute_steps(u'''
        When I visit "plea/enter_urn/"
        And I submit a valid welsh URN in english
        And I fill in "number_of_charges" with "1"
        And I fill in correct date of birth
        And I press "Continue"
    ''')

@given(u'I have validated a company URN')
def step_impl(context):
    context.execute_steps(u'''
        When I visit "plea/enter_urn/"
        And I submit a valid URN as company
        And I submit 1 charge and correct postcode
    ''')


@given(u'I have submitted my personal information')
def step_impl(context):
    context.execute_steps(u'''
        When I enter my name and contact details
        And I confirm my address as correct
        And I don't provide National Insurance number
        And I provide a reason for not having a National Insurance number
        And I don't provide UK driving licence number
        And I press "Continue"
    ''')


@given(u'I have pleaded guilty to both charges')
def step_impl(context):
    context.execute_steps(u'''
        When I plea guilty, and choose not to attend court
        When I plea guilty, and choose not to attend court
    ''')


@given(u'I have submitted my employment details')
def step_impl(context):
    context.execute_steps(u'''
        When I submit my employment status as "Employed"
        And I submit my home pay amount
        When I choose no hardship
        And I press "Continue"
    ''')

@when(u'I visit "{url}"')
def step_impl(context, url):
    if url.startswith("http://") or url.startswith("https://"):
        full_url = url
    else:
        full_url = context.base_url + '/' + url.lstrip('/')
    context.browser.get(full_url)

@when(u'I press "{button_text}"')
def step_impl(context, button_text):
    button = WebDriverWait(context.browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{button_text}')]"))
    )
    button.click()

@then(u'I should see "{text}"')
def step_impl(context, text):
    # Escape single quotes in the text
    escaped_text = text.replace("'", "\\'")
    xpath = f"//*[contains(text(), '{escaped_text}')]"
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

@then(u'I should not see "{text}"')
def step_impl(context, text):
    # Escape single quotes in the text
    escaped_text = text.replace("'", "\\'")
    xpath = f"//*[contains(text(), '{escaped_text}')]"
    WebDriverWait(context.browser, 10).until(
        EC.invisibility_of_element_located((By.XPATH, xpath))
    )

@when(u'I fill in "{field_name}" with "{value}"')
def step_impl(context, field_name, value):
    field = context.browser.find_element(By.ID, f"id_{field_name}")
    field.clear()
    field.send_keys(value)

@then(u'I should not see an element with id "{element_id}"')
def step_impl(context, element_id):
    assert context.browser.find_elements(By.ID, element_id) == []
