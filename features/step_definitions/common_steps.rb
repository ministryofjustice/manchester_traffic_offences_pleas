When(/^I click on continue$/) do
  common_page.button.click
end

Then(/^I should see '([^\"]*)' header$/) do |header|
  expect(common_page.content_header.h1.text).to eq header
end

Then(/^I should see second header '([^\"]*)'$/) do |header|
  expect(common_page.h2.text).to eq header
end

Then(/^I should see error message '([^\"]*)' with link ([^\"]*)$/) do |error_message, error_link|
  error_group = common_page.error_summary
  expect(error_group.h1[0].text).to eq 'You need to fix the errors on this page before continuing.'
  expect(error_group.p[0].text).to eq 'See highlighted errors below.'
  expect(error_group.link[0].text).to have_content error_message
  expect(error_group.link[0]['href']).to end_with error_link
end

Then(/^I should see second error message '([^\"]*)' with link ([^\"]*)$/) do |error_message, error_link|
  expect(common_page.error_summary.link[1].text).to have_content error_message
  expect(common_page.error_summary.link[1]['href']).to end_with error_link
end

Then(/^I am taken to ([^\"]*)$/) do |page_url|
  expect(common_page.current_path).to end_with page_url
end

Then(/^I should see make a plea by post error message$/) do
  error_group = common_page.error_summary
  expect(error_group.h1[1].text).to eq 'Make a plea by post'
  expect(error_group.p[1].text).to end_with 'please submit your plea by post using the forms enclosed.'
end

Then(/^I should not see other error messages$/) do
  expect(common_page.error_summary.link.count).to eq 1
end

Then(/^I should see the help image$/) do
  expect(common_page).to have_help_image
end

Then(/^I should see more information '([^\"]*)'$/) do |header_p|
  expect(common_page.content_header.p.text).to have_content header_p
end

Then(/^I should see error <message> with <link>$/) do |error_messages|
  error_group = common_page.error_summary
  expect(error_group.h1[0].text).to eq 'You need to fix the errors on this page before continuing.'
  expect(error_group.p[0].text).to eq 'See highlighted errors below.'
  error_messages.rows.each_with_index do |error, index|
    expect(error_group.link[index].text).to have_content error[0]
    expect(error_group.link[index]['href']).to end_with error[1]
  end
end
