@when(u'I enter my name and contact details')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "first_name" with "$first_name"
        And I fill in "last_name" with "$last_name"
        And I fill in "contact_number" with "$contact_number"
        And I fill in "email" with "$email"
    ''')


@when(u'I confirm my address as correct')
def step_impl(context):
    context.execute_steps(u'When I choose "True" from "correct_address"')


@when(u'I don\'t provide National Insurance number')
def step_impl(context):
    context.execute_steps(u'When I choose "False" from "have_ni_number"')

@when(u'I provide a reason for not having a National Insurance number')
def step_impl(context):
    context.execute_steps(u'When I fill in "no_ni_number_reason" with "$no_ni_number_reason"')

@when(u'I don\'t provide UK driving licence number')
def step_impl(context):
    context.execute_steps(u'When I choose "False" from "have_driving_licence_number"')


@then(u'I should be given a chance to plea to the first charge')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/plea/1"
        And I should see "Your plea for this charge"
    ''')


@when(u'I enter my company information')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "company_name" with "$company_name"
        And I choose "$position_in_company" from "position_in_company"
    ''')


@when(u'I choose to provide National Insurance number')
def step_impl(context):
    context.execute_steps(u'When I choose "True" from "have_ni_number"')


@when(u'I choose to provide UK driving licence')
def step_impl(context):
    context.execute_steps(u'When I choose "True" from "have_driving_licence_number"')


@when(u'I chose my address is incorrect')
def step_impl(context):
    context.execute_steps(u'When I choose "False" from "correct_address"')
