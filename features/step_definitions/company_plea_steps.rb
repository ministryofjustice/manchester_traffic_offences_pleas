Given(/^I visit the company plea page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
  step 'I select Single Justice Procedure Notice'
  step 'I successfully fill out the form on the behalf of a company'
  step 'I successfully submit the company details'
  step 'I click on continue'
end

Then(/^I should see present the company's case copy$/) do
  plea_group = your_plea_page.panel_grey
  expect(plea_group.p.text).to start_with 'This is your opportunity to present the company\'s case'
  expect(plea_group.li[0].text).to start_with 'the charge details and witness statements'
  expect(plea_group.li[1].text).to eq 'each offence may result in a fine'
  expect(plea_group.li[2].text).to have_content 'the company may get a 33% reduction'
end

Then(/^I should see pleading guilty to this charge means copy$/) do
  guilty_group = company_plea_page.panel_indent.p[0]
  expect(guilty_group.text).to have_content 'means a company representative does not need to come to court'
end

Then(/^I should see pleading not guilty to this charge means copy$/) do
  not_guilty_group = company_plea_page.panel_indent.p[1]
  expect(not_guilty_group.text).to have_content 'means we\'ll send details of a date for a company representative'
end

Then(/^I should see tell us why you believe the company is not guilty label$/) do
  hint_group = company_plea_page.section_not_guilty_extra.form_hint
  expect(hint_group.text).to eq 'Tell us why you believe the company is not guilty:'
end

Then(/^I should see does your company representative need an interpreter in court$/) do
  label_group = company_plea_page.label_interpreter_needed.label_text
  expect(label_group.text).to eq 'Does your company representative need an interpreter in court?'
end
