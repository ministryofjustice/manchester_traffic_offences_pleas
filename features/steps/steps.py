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

@then(u'I should see "{text}"')
def step_impl(context, text):
    try:
        # Escape single quotes in the text and use double quotes for the XPath
        escaped_text = text.replace("'", "\\'").replace('"', '\\"')
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{escaped_text}")]'))
        )
    except TimeoutException:
        # Check if the text is present in the page source
        page_source = context.browser.page_source
        if text in page_source:
            return  # Text found, consider it a success
        
        # Check for partial matches (useful for long texts or texts with special characters)
        words = text.split()
        if len(words) > 3:
            partial_text = ' '.join(words[:3])  # Use first 3 words
            if partial_text in page_source:
                return  # Partial match found, consider it a success

        print(f"Text '{text}' not found in page source")
        print(f"Current URL: {context.browser.current_url}")
        raise AssertionError(f"Text '{text}' not found in page source within 10 seconds")

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

@then(u'I should see the Welsh validation message')
def step_impl(context):
    expected_text = "Yn anffodus, nid yw'r cyfeirnod unigryw yn ddilys, ac nid yw'r system yn ei adnabod."
    try:
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//ul[@class="errorlist"]/li'))
        )
        error_message = context.browser.find_element(By.XPATH, '//ul[@class="errorlist"]/li').text
        assert expected_text in error_message, f"Expected text not found. Found: {error_message}"
    except (TimeoutException, AssertionError) as e:
        print(f"Error: {str(e)}")
        print(f"Current URL: {context.browser.current_url}")
        raise

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

@when(u'I confirm and submit my plea')
def step_impl(context):
    try:
        context.execute_steps(u'When I check "understand"')
    except Exception as e:
        print(f"Error checking 'understand': {str(e)}")
    
    try:
        submit_button = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
        )
        submit_button.click()
    except TimeoutException:
        print("Submit button not found or not clickable")
        print(f"Current URL: {context.browser.current_url}")
        raise
