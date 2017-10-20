When(/^I select guilty to one charge$/) do
  common_page.guilty.click
  panel_group = your_plea_guilty_page.panel_indent
  expect(panel_group.p[0].text).to start_with 'Pleading guilty to this charge means'
end

When(/^I select guilty to three charges$/) do
  common_page.guilty.click
end

When(/^I select yes to the guilty questions$/) do
  common_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
end

And(/^I successfully fill out the guilty form$/) do
  common_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  language_group.id_sjp_interpreter_language.set 'German'
  common_page.button.click
end

Then(/^I should see do you want to come to court to plead guilty$/) do
  common_page.guilty.click
  plea = your_plea_guilty_page.panel_indent
  expect(plea.label_come_to_court.text).to eq 'Do you want to come to court to plead guilty?'
  expect(your_plea_guilty_page.block_label[2].text).to eq 'Yes'
  expect(plea.come_to_court_true['type']).to eq 'radio'
  your_plea_guilty_page.panel_indent.come_to_court_true.click
end

Then(/^I should see do you need an interpreter in court$/) do
  common_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  label_group = your_plea_guilty_page.label_sjp_interpreter_needed.label_text
  expect(label_group.text).to eq 'Do you need an interpreter in court?'
  expect(your_plea_guilty_page.block_label[4].text).to eq 'Yes'
  expect(your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true['type']).to eq 'radio'
  expect(your_plea_guilty_page.block_label[5].text).to eq 'No'
  expect(your_plea_guilty_page.block_label[5].id_sjp_interpreter_needed_false['type']).to eq 'radio'
end

Then(/^I should see tell us which language copy$/) do
  common_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  language_group = your_plea_guilty_page.section_sjp_interpreter_language
  expect(language_group.form_hint.text).to eq 'If yes, tell us which language (include sign language):'
end

Then(/^I should see mitigation for guilty$/) do
  common_page.guilty.click
  your_plea_guilty_page.panel_indent.come_to_court_true.click
  your_plea_guilty_page.block_label[4].id_sjp_interpreter_needed_true.click
  guilty_extra = your_plea_guilty_page.section_guilty_extra
  expect(guilty_extra.label_text.text).to eq 'Mitigation'
  expect(guilty_extra.id_guilty_extra['type']).to eq 'textarea'
  expect(guilty_extra.form_hint_inline.text).to eq '(optional)'
  expect(guilty_extra.form_hint.text).to start_with 'Is there something you'
end
