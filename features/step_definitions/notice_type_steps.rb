Given(/^I visit the notice type page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
end

When(/^I select Single Justice Procedure Notice$/) do
  expect(notice_type_page.block_label[0].sjp_true['type']).to eq 'radio'
  expect(notice_type_page.block_label[0].text).to eq 'Single Justice Procedure Notice'
  notice_type_page.block_label[0].sjp_true.click
  common_page.button.click
end

When(/^I select something else$/) do
  expect(notice_type_page.block_label[1].sjp_false['type']).to eq 'radio'
  expect(notice_type_page.block_label[1].text).to eq 'Something else'
  notice_type_page.block_label[1].sjp_false.click
  common_page.button.click
end

Then(/^I should see what is the title label$/) do
  expect(notice_type_page.label_sjp.text).to start_with 'What is the title'
end
