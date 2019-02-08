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
    context.execute_steps(u'When I choose "False" from "hardship"')


@then(u'I should see my calculated weekly income of "{amount}"')
def step_impl(context, amount):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/your_income/"
        And I should see "Total weekly income"
        And I should see "%s"
    ''' % str(amount))


@then(u'I should see be asked to review my plea')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/review/"
        And I should see "Review the information you've given before making your pleas."
    ''')
