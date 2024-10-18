from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse

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
    try:
        context.execute_steps(u'''
            When I submit my employment status as "Employed"
            And I choose "Monthly" from "pay_period"
            And I enter "4000" in "income"
        ''')
    except Exception as e:
        print(f"Error submitting employment details: {str(e)}")
        print(f"Current URL: {context.browser.current_url}")
        raise

@when(u'I visit "{url}"')
def step_impl(context, url):
    if url.startswith("http://") or url.startswith("https://"):
        full_url = url
    else:
        full_url = context.base_url + '/' + url.lstrip('/')
    context.browser.get(full_url)
    print(f"Visiting URL: {full_url}")  # Add this line for debugging

@when(u'I press "{button_text}"')
def step_impl(context, button_text):
    try:
        # Try to find a button first
        element = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{button_text}')]"))
        )
    except TimeoutException:
        # If button is not found, try to find a link
        try:
            element = WebDriverWait(context.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{button_text}')]"))
            )
        except TimeoutException:
            print(f"Neither button nor link with text '{button_text}' found")
            print(f"Current URL: {context.browser.current_url}")
            raise
    
    element.click()

@then(u'I should not see "{text}"')
def step_impl(context, text):
    assert text not in context.browser.page_source, f"Text '{text}' found in page source, but it shouldn't be there"

@when(u'I fill in "{field_name}" with "{value}"')
def step_impl(context, field_name, value):
    field = context.browser.find_element(By.ID, f"id_{field_name}")
    field.clear()
    field.send_keys(value)

@then(u'I should not see an element with id "{element_id}"')
def step_impl(context, element_id):
    assert context.browser.find_elements(By.ID, element_id) == []

@when(u'I choose "{option}" from "{select_name}"')
def step_impl(context, option, select_name):
    try:
        # Replace variables with actual values from context.persona
        if option.startswith('$'):
            option = context.persona.get(option[1:], option)
        if select_name.startswith('$'):
            select_name = context.persona.get(select_name[1:], select_name)

        print(f"Choosing option: {option} from {select_name}")  # Debug print

        # Wait for the element to be present
        try:
            element = WebDriverWait(context.browser, 10).until(
                EC.presence_of_element_located((By.NAME, select_name))
            )
        except TimeoutException:
            print(f"Element with name '{select_name}' not found")
            print(f"Current URL: {context.browser.current_url}")
            raise

        # Check if it's a select element or radio button
        if element.tag_name == "select":
            select = Select(element)
            select.select_by_visible_text(option)
        else:
            # Assume it's a radio button
            radio = context.browser.find_element(By.CSS_SELECTOR, f'input[name="{select_name}"][value="{option}"]')
            radio.click()
    except Exception as e:
        print(f"Error choosing option: {str(e)}")
        print(f"Option: {option}, Select Name: {select_name}")
        print(f"Current URL: {context.browser.current_url}")
        raise

@when(u'I enter my name and contact details')
def step_impl(context):
    persona = context.persona
    context.execute_steps(u'''
        When I fill in "first_name" with "{}"
        And I fill in "last_name" with "{}"
        And I fill in "email" with "{}"
        And I fill in "contact_number" with "{}"
        And I press "Continue"
    '''.format(
        persona['first_name'],
        persona['last_name'],
        persona['email'],
        persona['contact_number']
    ))

@when(u'I confirm my address as correct')
def step_impl(context):
    try:
        # Wait for the radio buttons to be present
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "correct_address"))
        )
        
        # Select the "Yes" option
        yes_option = context.browser.find_element(By.CSS_SELECTOR, 'input[name="correct_address"][value="True"]')
        yes_option.click()
        
        # Click the "Continue" button
        continue_button = context.browser.find_element(By.XPATH, '//button[contains(text(), "Continue")]')
        continue_button.click()
    except Exception as e:
        print(f"Error confirming address: {str(e)}")
        print(f"Current URL: {context.browser.current_url}")
        
        # Additional debugging information
        try:
            form_errors = context.browser.find_elements(By.CLASS_NAME, "errorlist")
            if form_errors:
                print("Form errors found:")
                for error in form_errors:
                    print(error.text)
        except:
            pass
        
        raise

@then(u'the browser\'s URL should be "{expected_path}"')
def step_impl(context, expected_path):
    current_url = context.browser.current_url
    parsed_url = urlparse(current_url)
    actual_path = parsed_url.path.lstrip('/')  # Remove leading slash
    
    assert actual_path == expected_path, f"Expected URL path to be '{expected_path}', but got '{actual_path}'"

@when(u'I check "{checkbox_name}"')
def step_impl(context, checkbox_name):
    try:
        checkbox = WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.ID, f"id_{checkbox_name}"))
        )
        if not checkbox.is_selected():
            checkbox.click()
    except TimeoutException:
        print(f"Checkbox '{checkbox_name}' not found")
        print(f"Current URL: {context.browser.current_url}")
        raise

@when(u'I enter "{value}" in "{field_name}"')
def step_impl(context, value, field_name):
    try:
        element = WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.ID, f"id_{field_name}"))
        )
        element.clear()
        element.send_keys(value)
    except TimeoutException:
        print(f"Field '{field_name}' not found on the page")
        print(f"Current URL: {context.browser.current_url}")
        raise AssertionError(f"Field '{field_name}' not found on the page")
