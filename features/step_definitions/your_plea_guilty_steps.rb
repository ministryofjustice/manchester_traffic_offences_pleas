When(/^I select guilty to one charge$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
  your_plea_guilty_page.guilty.click
  panel_group = your_plea_guilty_page.panel_indent
  expect(panel_group.p[0].text).to have_content 'we\'ll send you details of the court\'s decision'
end

When(/^I select guilty to three charges$/) do
  step 'I successfully fill out the form with three charges against me'
  step 'I successfully submit my details'
  your_plea_guilty_page.guilty.click
  panel_group = your_plea_guilty_page.panel_indent
  expect(panel_group.p[0].text).to have_content 'we\'ll send you details of the court\'s decision'
end

When(/^I select yes to the guilty questions$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
  your_plea_guilty_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
end

And(/^I successfully fill out the guilty form$/) do
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  language_group.id_sjp_interpreter_language.set 'German'
  common_page.button.click
end

Then(/^I should see do you want to come to court to plead guilty$/) do
  plea = your_plea_guilty_page.panel_indent
  expect(plea.label_come_to_court.text).to eq 'Do you want to come to court to plead guilty?'
  expect(your_plea_guilty_page.block_label[2].text).to eq 'Yes'
  expect(plea.come_to_court_true['type']).to eq 'radio'
  your_plea_guilty_page.panel_indent.come_to_court_true.click
end

Then(/^I should see do you need an interpreter in court$/) do
  label_group = your_plea_guilty_page.label_sjp_interpreter_needed.label_text
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  expect(label_group.text).to eq 'Do you need an interpreter in court?'
  expect(your_plea_guilty_page.block_label[4].text).to eq 'Yes'
  expect(your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true['type']).to eq 'radio'
  expect(your_plea_guilty_page.block_label[5].text).to eq 'No'
  expect(your_plea_guilty_page.block_label[5].id_sjp_interpreter_needed_false['type']).to eq 'radio'
end

Then(/^I should see tell us which language copy$/) do
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  expect(language_group.form_hint.text).to eq 'If yes, tell us which language (include sign language):'
end

Then(/^I should see mitigation for guilty$/) do
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  guilty_extra = your_plea_guilty_page.section_guilty_extra
  expect(guilty_extra.label_text.text).to eq 'Mitigation'
  expect(guilty_extra.id_guilty_extra['type']).to eq 'textarea'
  expect(guilty_extra.form_hint_inline.text).to eq '(optional)'
  expect(guilty_extra.form_hint.text).to start_with 'Is there something you'
end
