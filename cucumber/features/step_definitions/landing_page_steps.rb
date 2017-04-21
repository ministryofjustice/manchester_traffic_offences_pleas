When(/^I visit the make a plea landing page$/) do
  landing_page.load_page()
end

When(/^I click on the start now button$/) do
  landing_page.content.start_now_button.click
end

Then(/^I should see page header$/) do
  expect(landing_page.content).to have_page_header
end

Then(/^I should be taken to your case page$/) do
  expect(your_case_page.content.page_header.text).to eq 'Your case'
end

