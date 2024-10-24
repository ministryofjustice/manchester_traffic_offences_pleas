import email
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from behave import then


@given(u'I have entered my personal details')
def step_impl(context):
    context.execute_steps(u'''
        When I enter "John" in "first_name"
        And I enter "Doe" in "last_name"
        And I enter "john.doe@example.com" in "email"
        And I enter "1234567890" in "contact_number"
    ''')
    context.email = "john.doe@example.com"
    context.first_name = "John"
    context.last_name = "Doe"
    context.contact_number = "1234567890"


@then(u'my details should match')
def step_impl(context):
    expected_details = [
        context.first_name,
        context.last_name,
        context.email,
        context.contact_number
    ]
    
    for detail in expected_details:
        try:
            WebDriverWait(context.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{detail}')]"))
            )
        except TimeoutException:
            print(f"Detail '{detail}' not found on the page")
            print(f"Current URL: {context.browser.current_url}")
            raise AssertionError(f"Detail '{detail}' not found on the page")


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
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(@value, 'Submit') or contains(@type, 'submit')]"))
        )
        submit_button.click()
    except TimeoutException as e:
        print(f"Error submitting plea: {str(e)}")
        print(f"Current URL: {context.browser.current_url}")
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
    # Ensure context.email is set before accessing it
    if not hasattr(context, 'email'):
        context.email = "default@example.com"  # Set a default email or handle appropriately

    # Ensure context.mail is set before accessing it
    if not hasattr(context, 'mail'):
        print("Error: context.mail is not set. Please ensure the mail context is initialized.")
        raise AssertionError("Mail context is not initialized.")

    print(f"Debug: Email in context is {context.email}")  # Debugging line
    context.execute_steps(u'''
        Then I should receive an email at "{}" with subject "Online plea submission confirmation"
    '''.format(context.email))
    
    persona = context.persona
    messages = context.mail.messages_for_user(context.email)  # Ensure this is the correct email

    # Check if messages are retrieved
    if not messages:
        raise AssertionError("No messages found for the user.")

    text = str(messages[0])  # Assuming messages is a list of dicts
    print(f"Debug: Email content: {text}")  # Print the email content for debugging

    # Check for the expected URN in the email content
    assert 'Your online pleas have been submitted' in text
    assert 'Your URN: {}'.format(persona['urn']) in text, f"Expected URN '{persona['urn']}' not found in email content."


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


@then(u'I should receive an email at "{email}" with subject "{subject}"')
def step_impl(context, email, subject):
    try:
        messages = context.mail.messages_for_user(email)
        assert len(messages) > 0, f"No emails received for {email}"
        
        found_subject = False
        for message in messages:
            if subject in message['subject']:
                found_subject = True
                break
        
        assert found_subject, f"Email with subject '{subject}' not found for {email}"
    except AssertionError as e:
        print(f"Error checking email: {str(e)}")
        print(f"Received messages: {messages}")
        raise

