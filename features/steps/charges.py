@when(u'I choose guilty - don\'t attend')
def step_impl(context):
    context.execute_steps(u'''
        When I choose "guilty_no_court" from "guilty"
    ''')

@when(u'I choose guilty - attend')
def step_impl(context):
    context.execute_steps(u'''
        When I choose "guilty_court" from "guilty"
    ''')


@when(u'I choose not guilty')
def step_impl(context):
    context.execute_steps(u'''
        When I choose "not_guilty" from "guilty"
    ''')


@when(u'I plea guilty, and choose not to attend court')
def step_impl(context):
    context.execute_steps(u'''
        When I choose guilty - don't attend
        And I press "Continue"
    ''')


@then(u'I should be asked for my employment status')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/your_status/"
        And I should see "Your employment status"
    ''')
