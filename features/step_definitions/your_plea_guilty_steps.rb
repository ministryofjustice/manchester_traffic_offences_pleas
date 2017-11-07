When(/^I select guilty to one charge$/) do
  common_page.id_guilty_guilty_court.click
end

When(/^I have one charge against me$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
  common_page.button.click
end

When(/^I have three charges against me$/) do
  step 'I successfully fill out the form with three charges against me'
  step 'I successfully submit my details'
  common_page.button.click
end

When(/^I select guilty - I want to attend court in person$/) do
  common_page.id_guilty_guilty_court.click
end

When(/^I select guilty - I want the case to be dealt with in my absence$/) do
  common_page.id_guilty_guilty_no_court.click
end

When(/^I select yes to the guilty questions$/) do
  common_page.id_guilty_guilty_court.click
  your_plea_guilty_page.block_label[3].id_sjp_interpreter_needed_true.click
end

And(/^I successfully fill out the guilty form$/) do
  common_page.id_guilty_guilty_court.click
  your_plea_guilty_page.block_label[3].id_sjp_interpreter_needed_true.click
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  language_group.id_sjp_interpreter_language.set 'German'
  common_page.button.click
end

Then(/^I should see do you need an interpreter in court$/) do
  common_page.id_guilty_guilty_court.click
  label_group = your_plea_guilty_page.label_sjp_interpreter_needed.label_text
  expect(label_group.text).to eq 'Do you need an interpreter in court?'
  expect(your_plea_guilty_page.block_label[3].text).to eq 'Yes'
  expect(your_plea_guilty_page.block_label[3].id_sjp_interpreter_needed_true['type']).to eq 'radio'
  expect(your_plea_guilty_page.block_label[4].text).to eq 'No'
  expect(your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_false['type']).to eq 'radio'
end

Then(/^I should see tell us which language copy$/) do
  common_page.id_guilty_guilty_court.click
  your_plea_guilty_page.block_label[3].id_sjp_interpreter_needed_true.click
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  expect(language_group.form_hint.text).to eq 'If yes, tell us which language (include sign language):'
end

Then(/^I should see mitigation for guilty$/) do
  guilty_extra = your_plea_guilty_page.section_guilty_extra
  expect(guilty_extra.label_text.text).to eq 'Mitigation'
  expect(guilty_extra.id_guilty_extra['type']).to eq 'textarea'
  expect(guilty_extra.form_hint_inline.text).to eq '(optional)'
  expect(guilty_extra.form_hint.text).to start_with 'Is there something you'
end
