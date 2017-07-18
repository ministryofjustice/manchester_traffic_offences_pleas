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

Then(/^I should see '([^\"]*)' header$/) do |header|
  expect(common_page.h1.text).to eq header
end

Then(/^I should see number of offences label$/) do
  expect(your_case_continued_page.label_text[0].text).to eq 'Number of offences'
end

Then(/^I should see date of birth label$/) do
  expect(your_case_continued_page.label_text[1].text).to eq 'Date of birth'
end

Then(/^I should not see date of birth label$/) do
  expect(your_case_continued_page).to should_not_have label_text[1]
end

Then(/^I should see number of offences hint$/) do
  expect(your_case_continued_page.form_hint[0].text).to eq 'How many offences are listed on your notice?'
end

Then(/^I should see error message '([^\"]*)'$/) do |error_message|
  error_summary = your_case_continued_page.error_summary
  error_list = your_case_continued_page.error_list

  expect(error_summary.h1.text).to eq 'You need to fix the errors on this page before continuing.'
  expect(error_summary.p.text).to eq 'See highlighted errors below.'
  expect(error_list[0].li.text).to eq error_message
end

Then(/^I should see second error message '([^\"]*)'$/) do |error_message|
  error_summary = your_case_continued_page.error_summary
  error_list = your_case_continued_page.error_list

  expect(error_summary.h1.text).to eq 'You need to fix the errors on this page before continuing.'
  expect(error_summary.p.text).to eq 'See highlighted errors below.'
  expect(error_list[1].li.text).to eq error_message
end

Then(/^I should be taken to your details page$/) do
  expect(current_path).to end_with '/plea/your_details/'
end

Then(/^I should not see postcode label$/) do
  expect(your_case_continued_page.label_text[0].text).to eq 'Postcode'
end

Then(/^I should not see postcode$/) do
  expect(your_case_continued_page.form_hint[1].text).to eq 'Postcode'
end
