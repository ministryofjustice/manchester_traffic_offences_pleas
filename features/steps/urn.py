def submit_urn(context, urn):
    context.execute_steps(u'''
        when I fill in "urn" with "%s"
        and I press "Continue"
    ''' % context.URNs[urn])


def submit_urn_in_welsh(context, urn):
    context.execute_steps(u'''
        when I fill in "urn" with "%s"
        and I press "Parhau"
    ''' % context.URNs[urn])


def submit_urn_region(context, urn):
    context.execute_steps(u'''
        when I fill in "urn" with "%s"
        and I press "Find my court"
    ''' % context.URNREGIONs[urn])


def submit_urn_court_finder(context, urn):
    context.execute_steps(u'''
           when I fill in "urn" with "%s"
           and I press "Find my court"
       ''' % context.URNs[urn])

@when(u'I submit a valid URN')
def step_impl(context):
    submit_urn(context, 'valid')

@when(u'I submit a valid english URN in welsh')
def step_impl(context):
    submit_urn_in_welsh(context, 'valid')

@when(u'I submit a valid URN as company')
def step_impl(context):
    submit_urn(context, 'company')


@when(u'I submit an invalid URN')
def step_impl(context):
    submit_urn(context, 'invalid')

@when(u'I submit a valid welsh URN in english')
def step_impl(context):
    submit_urn(context, 'valid_welsh')

@when(u'I submit a valid welsh URN in welsh')
def step_impl(context):
    submit_urn_in_welsh(context, 'valid_welsh')


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


@then(u'I should remain on the enter urn page')
def step_impl(context):
    context.execute_steps(u'''
        Then the browser's URL should be "plea/enter_urn/"
    ''')


@then(u'I should be asked to validate my date of birth')
def step_impl(context):
    step_impl(context, "plea/your_case_continued/")
    assert "Date of birth" in context.browser.page_source
    assert "Postcode" not in context.browser.page_source

@then(u'I should be asked to validate my postcode')
def step_impl(context):
    step_impl(context, "plea/your_case_continued/")
    assert "Postcode" in context.browser.page_source
    assert "Date of birth" not in context.browser.page_source

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
    step_impl(context, "plea/your_details/")
    assert "We need these in case we have to get in touch with you about your plea." in context.browser.page_source

@then(u'I should be asked for my company details')
def step_impl(context):
    step_impl(context, "plea/company_details/")
    assert "You can only make a plea on behalf of a company if you are a director" in context.browser.page_source

@when(u'I submit a valid URN for court finder')
def step_impl(context):
    submit_urn_court_finder(context, 'valid')


@when(u'I submit an invalid URN for court finder')
def step_impl(context):
    submit_urn_court_finder(context, 'invalid')


@when(u'I submit valid court code with invalid URN')
def step_impl(context):
    submit_urn_court_finder(context, 'invalid_with_valid_region')


@when(u'I submit a valid court code')
def step_impl(context):
    submit_urn_region(context, 'valid')


@when(u'I submit an invalid court code')
def step_impl(context):
    submit_urn_region(context, 'invalid')

