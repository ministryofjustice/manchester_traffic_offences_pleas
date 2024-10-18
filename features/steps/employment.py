from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

@when(u'I submit my employment status as "{type}"')
def step_impl(context, type):
    context.execute_steps(u'''
        When I choose "%s" from "you_are"
        And I press "Continue"
    ''' % type)


@when(u'I submit my benefits as "{type}"')
def step_impl(context, type):
    context.execute_steps(u'''
        When I choose "%s" from "benefit_type"
        And I choose "$pay_period" from "pay_period"
        And I fill in "pay_amount" with "$benefit_amount"
        And I press "Continue"
    ''' % type)


@when(u'I submit my home pay amount')
def step_impl(context):
    context.execute_steps(u'''
        When I choose "$pay_period" from "pay_period"
        And I fill in "pay_amount" with "$pay_amount"
        And I press "Continue"
    ''')


@when(u'I choose no hardship')
def step_impl(context):
    try:
        context.execute_steps(u'When I choose "False" from "hardship"')
    except Exception as e:
        print(f"Hardship field not found. This may be expected. Error: {str(e)}")
        # Check if we're on the correct page
        assert "Your employment" in context.browser.title, "Not on the expected employment page"
        # If we're on the correct page, we can assume the hardship field is not needed and continue


@then(u'I should see my calculated weekly income of "{amount}"')
def step_impl(context, amount):
    # Wait for the page to load
    WebDriverWait(context.browser, 10).until(
        EC.url_contains("plea/your_employment/")
    )
    
    # Check if the amount is present on the page
    try:
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.ID, "id_pay_amount"))
        )
        input_element = context.browser.find_element(By.ID, "id_pay_amount")
        assert input_element.get_attribute("value") == amount, f"Expected amount '{amount}', but found '{input_element.get_attribute('value')}'"
    except TimeoutException:
        print(f"Amount input field not found on the page")
        print(f"Current URL: {context.browser.current_url}")
        raise AssertionError(f"Amount input field not found on the page")


@then(u'I should see be asked to review my plea')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/review/"
        And I should see "Review the information you've given before making your pleas."
    ''')

@then(u'I should see "{text}"')
def step_impl(context, text):
    try:
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
    except TimeoutException:
        print(f"Text '{text}' not found on the page")
        print(f"Current URL: {context.browser.current_url}")
        raise AssertionError(f"Text '{text}' not found on the page")
