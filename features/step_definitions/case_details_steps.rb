Given(/^I visit the case details page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
  step 'I select Single Justice Procedure Notice'
end

When(/^I fill out my case details without providing a date$/) do
  case_details_page.id_number_of_charges.set '1'
  case_details_page.plea_made_by_defendant.click
  common_page.button.click
end

When(/^I fill out my case details without providing the number of charges$/) do
  case_details_page.day.set('11')
  case_details_page.month.set('09')
  case_details_page.year.set('2017')
  case_details_page.plea_made_by_defendant.click
  common_page.button.click
end

When(/^I fill out my case details without selecting plea made by option$/) do
  case_details_page.id_number_of_charges.set '1'
  case_details_page.day.set('11')
  case_details_page.month.set('09')
  case_details_page.year.set('2017')
  common_page.button.click
end

When(/^I successfully fill out the form with three charges against me$/) do
  case_details_page.id_number_of_charges.set '3'
  case_details_page.day.set('11')
  case_details_page.month.set('09')
  case_details_page.year.set('2017')
  case_details_page.plea_made_by_defendant.click
  common_page.button.click
end

Then(/^I should see posting date label$/) do
  expect(case_details_page.posting_date.label_text.text).to eq 'Posting date'
end

Then(/^I should see posting date hint$/) do
  expect(case_details_page.posting_date.form_hint.text).to start_with 'On page 1 of the notice'
end

Then(/^I should see offences label$/) do
  expect(case_details_page.number_of_charges.label_text.text).to eq 'Number of offences'
end

Then(/^I should see offences hint$/) do
  expect(case_details_page.number_of_charges.form_hint.text).to eq 'How many offences are listed on your notice?'
end

Then(/^I should see are you label$/) do
  expect(case_details_page.section_plea_made_by.label_text.text).to eq 'Are you?'
end

Then(/^I should see are you hint$/) do
  expect(case_details_page.section_plea_made_by.form_hint.text).to eq 'Choose one of the following options:'
end

When(/^I successfully fill out the form as the person named in the notice$/) do
  case_details_page.id_number_of_charges.set '1'
  case_details_page.day.set('11')
  case_details_page.month.set('09')
  case_details_page.year.set('2017')
  expect(case_details_page.plea_made_by_defendant['type']).to eq 'radio'
  case_details_page.plea_made_by_defendant.click
  common_page.button.click
end

When(/^I successfully fill out the form on the behalf of a company$/) do
  case_details_page.id_number_of_charges.set '1'
  case_details_page.day.set('11')
  case_details_page.month.set('09')
  case_details_page.year.set('2017')
  expect(case_details_page.plea_made_by_company_rep['type']).to eq 'radio'
  case_details_page.plea_made_by_company_rep.click
  common_page.button.click
end
