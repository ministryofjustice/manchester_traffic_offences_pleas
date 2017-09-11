Given(/^I visit the enter urn page$/) do
  enter_urn_page.load_page
end

When(/^I enter an invalid URN$/) do
  enter_urn_page.section_urn.urn_field.set('HDNFH74757')
  enter_urn_page.continue_button.click
end

When(/^I enter a valid URN$/) do
  enter_urn_page.section_urn.urn_field.set('51GH6735264')
  enter_urn_page.continue_button.click
end

When(/^I enter an invalid URN three times$/) do
  3.times do
    enter_urn_page.section_urn.urn_field.set('HDNFH74757')
    enter_urn_page.continue_button.click
  end
end

Then(/^I should see provide URN hint$/) do
  expect(enter_urn_page.section_urn).to have_text
  expect(enter_urn_page.section_urn).to have_hint
end

Then(/^I should see make a plea by post error message$/) do
  expect(common_page.error_summary.h1[1].text).to eq 'Make a plea by post'
  expect(common_page.error_summary.p[1].text).to end_with 'please submit your plea by post using the forms enclosed.'
end
