When(/^I click on continue$/) do
  your_case_continued_page.button.click
end

Then(/^I should see '([^\"]*)' header$/) do |header|
  expect(common_page.h1.text).to eq header
end

Then(/^I should see error message '([^\"]*)'$/) do |error_message|
  expect(common_page.error_summary.h1[0].text).to eq 'You need to fix the errors on this page before continuing.'
  expect(common_page.error_summary.p[0].text).to eq 'See highlighted errors below.'
  expect(common_page.error_summary.link.text).to start_with error_message
end

Then(/^I should see error link '([^\"]*)'$/) do |error_link|
  expect(common_page.error_summary.link['href']).to end_with error_link
end

Then(/^I am taken to ([^\"]*)$/) do |page_url|
  expect(common_page.current_path).to end_with page_url
end
