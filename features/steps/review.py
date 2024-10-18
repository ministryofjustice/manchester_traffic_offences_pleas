import email
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@then(u'my details should match')
def step_impl(context):
    context.execute_steps(u'''
        Then I should see "$first_name"
        And I should see "$last_name"
        And I should see "$contact_number"
        And I should see "$email"
    ''')


@when(u'I confirm and submit my plea')
def step_impl(context):
    try:
        # Check the "understand" checkbox if it exists
        try:
            checkbox = WebDriverWait(context.browser, 10).until(
                EC.presence_of_element_located((By.ID, "id_understand"))
            )
            if not checkbox.is_selected():
                checkbox.click()
        except TimeoutException:
            print("'Understand' checkbox not found. Continuing...")

        # Find and click the submit button
        submit_button = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(@value, 'Submit')]"))
        )
        submit_button.click()
    except TimeoutException as e:
        print(f"Error submitting plea: {str(e)}")
        print(f"Current URL: {context.browser.current_url}")
        print(f"Page source:\n{context.browser.page_source}")
        raise


@then(u'I should see the confirmation page')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/complete/"
        And I should see "Your pleas have been sent to the magistrate"
        And I should see "Your URN: $urn"
    ''')


@then(u'I should receive the confirmation email')
def step_impl(context):
    context.execute_steps(u'''
        Then I should receive an email at "$email" with subject "Online plea submission confirmation"
        # And I should receive an email at "$email" containing "Your online pleas have been submitted"
    ''')
    # the above behaving step is failing in library code
    persona = context.persona
    messages = context.mail.messages_for_user(persona['email'])
    text = str(messages[0])
    assert 'Your online pleas have been submitted' in text
    assert 'Your URN: {}'.format(persona['urn']) in text


@then(u'police should receive confirmation email')
def step_impl(context):
    context.execute_steps(u'''
        Then I should receive an email at "police@example.com" with subject "POLICE ONLINE PLEA: 00/FF/12345/60 <SJP> SMITH John"
    ''')


@then(u'the court should receive my plea email with attached details')
def step_impl(context):
    persona = context.persona
    name = "{} {}".format(persona['last_name'].upper(), persona['first_name'])
    context.execute_steps(u'''
        Then I should receive an email at "court@example.com" with subject "ONLINE PLEA: $urn <SJP> %s"
        And I should receive an email at "court@example.com" with attachment "plea.html"
    ''' % name)

    messages = context.mail.messages_for_user('court@example.com')
    attachment = email.message_from_string(messages[0]).get_payload(1)
    text = str(attachment)

    assert persona['first_name'] in text
    assert persona['last_name'] in text
    assert persona['email'] in text
    assert persona['contact_number'] in text
    assert persona['urn'] in text

    assert 'Charge 1' in text
    assert 'Charge 2' in text
    assert 'Your employment status' in text
    assert 'Total weekly income' in text
