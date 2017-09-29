When(/^I select not guilty to one charge$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
  your_plea_not_guilty_page.not_guilty.click
  panel_group = your_plea_not_guilty_page.panel_indent
  expect(panel_group.p[1].text).to have_content 'we\'ll send details of a date for you to come to court'
end

When(/^I select not guilty to three charges$/) do
  step 'I successfully fill out the form with three charges against me'
  step 'I successfully submit my details'
  your_plea_not_guilty_page.not_guilty.click
  panel_group = your_plea_not_guilty_page.panel_indent
  expect(panel_group.p[1].text).to have_content 'we\'ll send details of a date for you to come to court'
end

When(/^I successfully fill out the not guilty form$/) do
  your_plea_not_guilty_page.section_not_guilty_extra.id_not_guilty_extra.set 'I was not the driver'
  your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true.click
  language_group = your_plea_not_guilty_page.section_interpreter_language
  language_group.id_interpreter_language.set 'German'
  your_plea_not_guilty_page.block_label[8].id_disagree_with_evidence_true.click
  evidence_details_group = your_plea_not_guilty_page.section_disagree_with_evidence_details
  evidence_details_group.id_disagree_with_evidence_details.set 'Paul Smith was the driver'
  your_plea_not_guilty_page.block_label[10].id_witness_needed_true.click
  witness_group = your_plea_not_guilty_page.section_witness_details
  witness_group.id_witness_details.set 'Paul Smith, 102 Petty France, London.  07777111222'
  your_plea_not_guilty_page.block_label[12].id_witness_interpreter_needed_true.click
  witness_language_group = your_plea_not_guilty_page.section_witness_interpreter_language
  witness_language_group.id_witness_interpreter_language.set 'German'
  common_page.button.click
end

Then(/^I should see do you need an interpreter in court header$/) do
  your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true.click
  label_group = your_plea_not_guilty_page.label_interpreter_needed.label_text
  expect(label_group.text).to eq 'Do you need an interpreter in court?'
end

And(/^it should display yes and no option an interpreter in court$/) do
  your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true.click
  expect(your_plea_not_guilty_page.block_label[6].text).to eq 'Yes'
  expect(your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true['type']).to eq 'radio'
  expect(your_plea_not_guilty_page.block_label[7].text).to eq 'No'
  expect(your_plea_not_guilty_page.block_label[7].id_interpreter_needed_false['type']).to eq 'radio'
end

And(/^yes should display tell us which language$/) do
  your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true.click
  language_group = your_plea_not_guilty_page.section_interpreter_language
  expect(language_group.form_hint.text).to eq 'If yes, tell us which language (include sign language):'
  expect(language_group.id_interpreter_language['type']).to eq 'text'
end

And(/^I select yes to the not guilty questions$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
  your_plea_not_guilty_page.not_guilty.click
  your_plea_not_guilty_page.block_label[6].id_interpreter_needed_true.click
  your_plea_not_guilty_page.block_label[8].id_disagree_with_evidence_true.click
  your_plea_not_guilty_page.block_label[10].id_witness_needed_true.click
  your_plea_not_guilty_page.block_label[12].id_witness_interpreter_needed_true.click
end

Then(/^I should see not guilty because copy$/) do
  extra_group = your_plea_not_guilty_page.section_not_guilty_extra
  expect(extra_group.label_text.text).to eq 'Not guilty because?'
  hint_group = your_plea_not_guilty_page.section_not_guilty_extra.form_hint
  expect(hint_group.text).to eq 'Why do you believe you are not guilty?'
end

Then(/^I should see evidence and witness header$/) do
  expect(your_plea_not_guilty_page.h3.text).to eq 'Evidence and witness information'
end

Then(/^I should see do you disagree with any evidence section$/) do
  your_plea_not_guilty_page.block_label[8].id_disagree_with_evidence_true.click
  disagree_group = your_plea_not_guilty_page.section_disagree_with_evidence.label_disagree_with_evidence
  expect(disagree_group.text).to start_with 'Do you disagree with any evidence from a witness statement'
end

And(/^it should display yes and no option for disagree with any evidence$/) do
  expect(your_plea_not_guilty_page.block_label[8].text).to eq 'Yes'
  expect(your_plea_not_guilty_page.block_label[8].id_disagree_with_evidence_true['type']).to eq 'radio'
  expect(your_plea_not_guilty_page.block_label[9].text).to eq 'No'
  expect(your_plea_not_guilty_page.block_label[9].id_disagree_with_evidence_false['type']).to eq 'radio'
end

When(/^I should see witness information$/) do
  your_plea_not_guilty_page.block_label[8].id_disagree_with_evidence_true.click
  evidence_details_group = your_plea_not_guilty_page.section_disagree_with_evidence_details
  expect(evidence_details_group.form_hint.text).to have_content 'If yes, tell us the name of the witness'
end
