from behave import given
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import resource
import os

PERSONAS = {
    'John': dict(
        first_name='John',
        middle_name='Bob',
        last_name='Smith',
        email='test@example.com',
        contact_number='0212345678',
        ni_number='XXX',
        no_ni_number_reason='Lost my NI card',
        driving_licence_number='YYY',
        company_name='MoJ',
        position_in_company='Director',
        pay_period='Monthly',
        pay_amount='4000',
        benefit_amount='2000',
        urn='00/FF/12345/60'
    ),
}
URNs = {
    'valid': '00FF1234560', # 2 offences
    'valid_welsh': '03FF1234560', # 1 offence
    'no_dob_no_postcode': '00FF1234561',
    'only_dob': '00FF1234562',
    'only_postcode': '00FF1234563',
    'company': '00FF1234564',
    'invalid': '1234',
    'inexistent': '00FF0000000',
    'invalid_with_valid_region': '00FG1122233'
}

URNREGIONs = {
    'valid': '00',
    'invalid': '99',
}

# override with -Dkey=value
config = {
    'base_url': 'http://127.0.0.1:8000',
    'headless': True,
    'remote': False,
}

def before_all(context):
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
    mail_dir = '/tmp/mailmock'
    context.mail_path = '/tmp/mailmock'
    if not os.path.exists(mail_dir):
        os.makedirs(mail_dir)

    config.update(context.config.userdata)

    if config['remote']:
        context.remote_webdriver = True
        s_username = os.environ['SAUCELABS_USER']
        s_apikey = os.environ['SAUCELABS_KEY']
        saucelabs_url = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (s_username, s_apikey)
        context.browser_args = {'url': saucelabs_url}
    else:
        context.default_browser = 'chrome'
        context.single_browser = True
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--remote-debugging-port=9222")
        context.browser_args = {'options': chrome_options}

    context.base_url = config['base_url']
    context.URNs = URNs
    context.URNREGIONs = URNREGIONs

def after_all(context):
    if hasattr(context, 'browser'):
        context.browser.quit()

def before_scenario(context, scenario):
    context.personas = PERSONAS
    context.execute_steps(u'''
        Given a browser
        And "John" as the persona
    ''')

def after_scenario(context, scenario):
    if hasattr(context, 'browser'):
        context.browser.quit()

@given(u'a browser')
def step_impl(context):
    context.browser = webdriver.Chrome(options=context.browser_args['options'])
