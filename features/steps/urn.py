def submit_urn(context, urn):
    context.execute_steps(u'''
        when I fill in "urn" with "%s"
        and I press "Continue"
    ''' % context.URNs[urn])


@when(u'I submit a valid URN')
def step_impl(context):
    submit_urn(context, 'valid')


@when(u'I submit a valid URN as company')
def step_impl(context):
    submit_urn(context, 'company')


@when(u'I submit an invalid URN')
def step_impl(context):
    submit_urn(context, 'invalid')


@when(u'I submit an inexistent URN')
def step_impl(context):
    submit_urn(context, 'inexistent')


@when(u'I submit a valid URN where only date of birth is known')
def step_impl(context):
    submit_urn(context, 'only_dob')


@when(u'I submit a valid URN where only postcode is known')
def step_impl(context):
    submit_urn(context, 'only_postcode')


@when(u'I submit a valid URN where date of birth and postcode are not known')
def step_impl(context):
    submit_urn(context, 'no_dob_no_postcode')


@then(u'I should be asked to validate my date of birth')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/your_case_continued/"
        And I should see "Date of birth"
        And I should not see "Postcode"
    ''')


@then(u'I should be asked to validate my postcode')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/your_case_continued/"
        And I should see "Postcode"
        And I should not see "Date of birth"
    ''')


@when(u'I submit an invalid URN three times')
def step_impl(context):
    for i in range(0,3):
        context.execute_steps(u'when I submit an invalid URN')


@when(u'I fill in correct date of birth')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "date_of_birth_0" with "11"
        And I fill in "date_of_birth_1" with "11"
        And I fill in "date_of_birth_2" with "1990"
    ''')


@when(u'I fill in incorrect date of birth')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "date_of_birth_0" with "11"
        And I fill in "date_of_birth_1" with "11"
        And I fill in "date_of_birth_2" with "1980"
    ''')


@when(u'I submit 1 charge and correct postcode')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "number_of_charges" with "1"
        And I fill in "postcode" with "C1 1CC"
        And I press "Continue"
    ''')


@when(u'I submit 1 charge and correct date of birth')
def step_impl(context):
    context.execute_steps(u'''
        When I fill in "number_of_charges" with "1"
        And I fill in correct date of birth
        And I press "Continue"
    ''')


@then(u'I should be asked for my personal details')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/your_details/"
        And I should see "We need these in case we have to get in touch with you about your plea."
    ''')


@then(u'I should be asked for my company details')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/company_details/"
        Then I should see "You can only make a plea on behalf of a company if you are a director"
    ''')
