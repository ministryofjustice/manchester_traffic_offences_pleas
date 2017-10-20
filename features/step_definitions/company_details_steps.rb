Given(/^I visit your company details page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
  step 'I select Single Justice Procedure Notice'
  step 'I successfully fill out the form on the behalf of a company'
end

Then(/^I should see we need these in case we have to contact you copy$/) do
  expect(common_page.content_header.p.text).to eq 'We need these in case we have to contact you about your plea.'
end

Then(/^I should see warning$/) do
  expect(company_details_page.panel_grey.heading_small.text).to eq 'Warning:'
  expect(company_details_page.panel_grey.p.text).to have_content 'make a plea on behalf of a company'
end

Then(/^I should be asked for the company name$/) do
  expect(company_details_page.form_group[0].label_text.text).to eq 'Company name'
  expect(company_details_page.form_group[0].form_hint.text).to eq 'As written on page 1 of the notice we sent you.'
  expect(company_details_page.section_company_name.id_company_name['type']).to eq 'text'
end

Then(/^I should be asked if the company address is correct$/) do
  correct_group = company_details_page.section_correct_address
  expect(correct_group.label_correct_address.text).to have_content 'Is the company\'s address correct on page 1'
  expect(correct_group.block_label[0].text).to eq 'Yes'
  expect(correct_group.block_label[0].id_correct_address_true['type']).to eq 'radio'
  expect(correct_group.block_label[1].text).to eq 'No'
  expect(correct_group.block_label[1].id_correct_address_false['type']).to eq 'radio'
end

Then(/^I should be asked your first name$/) do
  expect(company_details_page.section_first_name.label_text.text).to eq 'Your first name'
  expect(company_details_page.section_first_name.id_first_name['type']).to eq 'text'
end

Then(/^I should be asked your last name$/) do
  expect(company_details_page.section_last_name.label_text.text).to eq 'Your last name'
  expect(company_details_page.section_last_name.id_last_name['type']).to eq 'text'
end

Then(/^I should be asked my position in the company$/) do
  company_group = company_details_page.section_position_in_company
  expect(company_group.label_position_in_company.text).to eq 'Your position in the company'
end

Then(/^I should be asked if I am the director$/) do
  company_group = company_details_page.section_position_in_company
  expect(company_group.block_label[0].text).to eq 'director'
  expect(company_group.id_position_director['type']).to eq 'radio'
end

Then(/^I should be asked if I am the company secretary$/) do
  company_group = company_details_page.section_position_in_company
  expect(company_group.block_label[1].text).to eq 'company secretary'
  expect(company_group.id_position_secretary['type']).to eq 'radio'
end

Then(/^I should be asked if I am the company solicitor$/) do
  company_group = company_details_page.section_position_in_company
  expect(company_group.block_label[2].text).to eq 'company solicitor'
  expect(company_group.id_position_solicitor['type']).to eq 'radio'
end

When(/^I successfully submit the company details$/) do
  company_details_page.section_company_name.id_company_name.set 'MoJ'
  company_details_page.section_correct_address.block_label[1].id_correct_address_false.click
  company_details_page.id_updated_address.set '102 Petty France, Westminster, London SW1H 9AJ'
  company_details_page.section_first_name.id_first_name.set 'John'
  company_details_page.section_last_name.id_last_name.set 'Smith'
  company_details_page.section_position_in_company.id_position_director.click
  company_details_page.section_contact_number.id_contact_number.set '07555118077'
  company_details_page.section_email.id_email.set 'j.smith@test.com'
end

Then(/^I should be asked for a contact number$/) do
  expect(company_details_page.form_group[5].label_text.text).to eq 'Contact number'
  expect(company_details_page.form_group[5].form_hint.text).to eq 'Office or mobile number.'
  expect(company_details_page.section_contact_number.id_contact_number['type']).to eq 'tel'
end

Then(/^I should be asked for my work email address$/) do
  expect(company_details_page.section_email.label_text.text).to eq 'Work email address'
  expect(company_details_page.section_email.form_hint.text).to eq 'We\'ll automatically email you a copy of your plea'
end
