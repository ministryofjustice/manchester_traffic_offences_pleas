@given(u'I have validated a personal URN')
def step_impl(context):
    context.execute_steps(u'''
        When I visit "plea/enter_urn/"
        And I submit a valid URN
        And I fill in "number_of_charges" with "2"
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
