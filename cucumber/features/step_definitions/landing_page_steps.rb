Given(/^I visit the make a plea landing page$/) do
  landing_page.load_page()
end

And(/^I see available in Welsh copy$/) do
  expect(landing_page.content.available_in_welsh.text).to eq 'This page is also available in Welsh (Cymraeg).'
end

When(/^I click on the start now button$/) do
  landing_page.content.start_now_button.click
end

When(/^I click on the Welsh copy link$/) do
  landing_page.content.available_in_welsh_link.click
end

Then(/^I should see page header$/) do
  expect(landing_page.content.page_header.text).to eq 'Make a plea for a traffic offence'
end

Then(/^I should see get started intro$/) do
  expect(landing_page.content).to have_get_started_intro
end

Then(/^I should be taken to "Your case" page$/) do
  expect(landing_page.content.page_header.text).to eq 'Your case'
end

Then(/^I should see make a plea for a traffic offence in Welsh$/) do
  expect(landing_page.content.page_header.text).to eq 'Cofnodi ple ar gyfer trosedd traffig'
end

Then(/^I should see before you start copy$/) do
  expect(landing_page.content).to have_before_you_start
end

Then(/^I should see link to contact the court$/) do
  expect(landing_page.content.before_you_start_link.text).to eq 'contact the court'
  expect(landing_page.content.before_you_start_link['href']).to end_with('/court-finder/')
end

Then(/^I should see link to get help with making a plea online$/) do
  expect(landing_page.content.get_help_link.text).to eq 'get help with making a plea online.'
  expect(landing_page.content.get_help_link['href']).to end_with('/helping-you-plead-online')
end
