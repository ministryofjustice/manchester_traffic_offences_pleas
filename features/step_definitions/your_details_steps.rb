def valid_name
  your_details_page.section_first_name.id_first_name.set 'John'
  your_details_page.section_middle_name.id_middle_name.set 'George'
  your_details_page.section_last_name.id_last_name.set 'Smith'
end

def valid_data
  valid_name
  your_details_page.section_contact_number.id_contact_number.set '0207514445'
  valid_date_of_birth
  your_details_page.section_email.id_email.set 'test@hmcts.net'
end

def valid_date_of_birth
  dob = your_details_page.section_date_of_birth
  dob.id_date_of_birth_0.set '07'
  dob.id_date_of_birth_1.set '03'
  dob.id_date_of_birth_2.set '1987'
end

def invalid_date_of_birth
  dob = your_details_page.section_date_of_birth
  dob.id_date_of_birth_0.set Date.today.day
  dob.id_date_of_birth_1.set Date.today.month
  dob.id_date_of_birth_2.set Date.today.year
end

Given(/^I visit your details page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
  step 'I select Single Justice Procedure Notice'
  step 'I successfully fill out the form as the person named in the notice'
end

When(/^I successfully submit my details$/) do
  valid_data
  your_details_page.id_correct_address_true.click
  your_details_page.id_have_ni_number_false.click
  your_details_page.id_have_driving_licence_number_false.click
  common_page.button.click
end

When(/^I click yes I have a National Insurance number$/) do
  valid_data
  your_details_page.id_correct_address_true.click
  your_details_page.id_have_ni_number_true.click
  your_details_page.id_have_driving_licence_number_false.click
  common_page.button.click
end

When(/^I enter my National Insurance number$/) do
  your_details_page.section_ni_number.id_ni_number.set 'JR053905D'
  common_page.button.click
end

When(/^I click yes I have a UK driving license$/) do
  valid_data
  your_details_page.id_correct_address_true.click
  your_details_page.id_have_ni_number_false.click
  your_details_page.id_have_driving_licence_number_true.click
  common_page.button.click
end

When(/^I enter my UK driving license number$/) do
  licence_group = your_details_page.section_driving_licence_number

  expect(licence_group.form_hint.text).to start_with 'If yes, enter it here.'
  expect(licence_group).to have_img
  licence_group.id_driving_licence_number.set 'SMITH80307J97812'
  common_page.button.click
end

When(/^I fill out the form I click no my address is not correct$/) do
  valid_data
  your_details_page.id_correct_address_false.click
  your_details_page.id_have_ni_number_false.click
  your_details_page.id_have_driving_licence_number_false.click
end

When(/^I fill out the form with a date of birth that is not before today$/) do
  valid_data
  your_details_page.id_correct_address_true.click
  invalid_date_of_birth
  your_details_page.id_have_ni_number_false.click
  your_details_page.id_have_driving_licence_number_false.click
  common_page.button.click
end

When(/^I enter my correct address$/) do
  address_group = your_details_page.section_updated_address

  expect(address_group.form_hint.text).to eq 'If no, tell us your correct address here:'
  address_group.id_updated_address.set '102 Petty France, London, SW1H 9AJ'
  common_page.button.click
end

Then(/^I should be asked for my first name$/) do
  expect(your_details_page.section_first_name.label_text.text).to eq 'First name'
end

Then(/^I should be asked for my middle name$/) do
  expect(your_details_page.section_middle_name.label_text.text).to eq 'Middle name'
end

Then(/^I should be asked for my last name$/) do
  expect(your_details_page.section_last_name.label_text.text).to eq 'Last name'
end

Then(/^I should be asked if my address is correct$/) do
  address_group = your_details_page.section_correct_address.label_text

  expect(address_group.text).to eq 'Is your address correct on page 1 of the notice we sent to you?'
  expect(your_details_page.id_correct_address_true['type']).to eq 'radio'
  expect(your_details_page.id_correct_address_false['type']).to eq 'radio'
end

Then(/^I should be asked for my contact number$/) do
  contact_group = your_details_page.section_contact_number

  expect(contact_group.label_text.text).to eq 'Contact number'
  expect(contact_group.form_hint.text).to eq 'Landline or mobile number.'
end

Then(/^I should be asked for my date of birth$/) do
  expect(your_details_page.section_date_of_birth.label_date_of_birth.text).to eq 'Date of birth'
end

Then(/^I should be asked for my email address$/) do
  expect(company_details_page.section_email.label_text.text).to eq 'Email address'
  expect(company_details_page.section_email.form_hint.text).to eq 'We\'ll automatically email you a copy of your plea'
end
