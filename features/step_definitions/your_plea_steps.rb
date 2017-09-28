Given(/^I visit your plea page$/) do
  step 'I visit the enter urn page'
  step 'I enter a valid URN'
  step 'I select Single Justice Procedure Notice'
end

When(/^I have one charge against me$/) do
  step 'I successfully fill out the form as the person named in the notice'
  step 'I successfully submit my details'
end

When(/^I have three charges against me$/) do
  step 'I successfully fill out the form with three charges against me'
  step 'I successfully submit my details'
end

Then(/^I should see plea options$/) do
  expect(your_plea_page.label_charge.label_text.text).to eq 'Your plea for charge 1'
  expect(your_plea_page.block_label[0].text).to eq 'Guilty'
  expect(your_plea_page.block_label[1].text).to eq 'Not guilty'
  expect(your_plea_page.guilty['type']).to eq 'radio'
  expect(your_plea_page.not_guilty['type']).to eq 'radio'
end

Then(/^I should see present your case copy$/) do
  plea_group = your_plea_page.panel_grey
  expect(plea_group.p.text).to eq 'This is your opportunity to present your case to the court:'
  expect(plea_group.li[0].text).to start_with 'the charge details and witness statements'
  expect(plea_group.li[1].text).to start_with 'each offence may carry penalty'
  expect(plea_group.li[2].text).to start_with 'if you plead guilty'
end
