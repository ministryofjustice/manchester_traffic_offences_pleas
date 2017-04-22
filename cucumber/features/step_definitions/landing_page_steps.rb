When(/^I visit the make a plea landing page$/) do
  landing_page.load_page()
end

When(/^I click on the start now button$/) do
  landing_page.content.start_now_button.click
end

Then(/^I should see page header$/) do
  expect(landing_page.content.page_header.text).to eq 'Make a plea for a traffic offence'
end

Then(/^I should see get started intro$/) do
  expect(landing_page.content).to have_get_started_intro
end

Then(/^I should be taken to "Your case" page$/) do
  expect(your_case_page.content.page_header.text).to eq 'Your case'
end

And(/^I should see "([^"]*)"$/) do |arg1|
  pending # Write code here that turns the phrase above into concrete actions
end