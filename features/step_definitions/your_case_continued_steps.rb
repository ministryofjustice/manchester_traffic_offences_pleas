Given(/^I visit the your case continued page$/) do
  step 'I visit the enter urn page'
end

And(/^my date of birth is not known$/) do
  enter_urn_page.section_urn.urn_field.set('51GH6735265')
  enter_urn_page.continue_button.click
end

When(/^my date of birth is known$/) do
  enter_urn_page.section_urn.urn_field.set('51GH6735264')
  enter_urn_page.continue_button.click
end

When(/^I enter ([^\"]*) into the number of offences input field$/) do |offences|
  your_case_continued_page.number_of_charges.set(offences)
end

When(/^I enter a valid date of birth$/) do
  your_case_continued_page.day.set('04')
  your_case_continued_page.month.set('05')
  your_case_continued_page.year.set('1978')
  your_case_continued_page.button.click
end

When(/^I enter ([^\"]*) as the postcode$/) do |postcode|
  your_case_continued_page.id_postcode.set(postcode)
  enter_urn_page.continue_button.click
end

Then(/^I should see number of offences label$/) do
  expect(your_case_continued_page.label_text[0].text).to eq 'Number of offences'
end

Then(/^I should see date of birth label$/) do
  expect(your_case_continued_page.label_text[1].text).to eq 'Date of birth'
end

Then(/^I should not see date of birth$/) do
  expect(your_case_continued_page).to have_no_section_date_of_birth
end

Then(/^I should see number of offences hint$/) do
  expect(your_case_continued_page.form_hint[0].text).to eq 'How many offences are listed on your notice?'
end

Then(/^I should not see postcode$/) do
  expect(your_case_continued_page).to have_no_id_postcode
end

Then(/^I should see postcode label$/) do
  expect(your_case_continued_page.label_text[1].text).to eq 'Postcode'
end

Then(/^I should see postcode hint$/) do
  expect(your_case_continued_page.form_hint[1].text).to eq 'As written on the notice we sent you'
end

Then(/^I should see check the details you've entered error message$/) do
  error_summary = your_case_continued_page.error_summary

  expect(error_summary.h1.text).to eq 'Check the details you\'ve entered'
  expect(error_summary.p.text).to eq 'The information you\'ve entered does not match our records.'
end
