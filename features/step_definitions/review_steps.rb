Given(/^I visit the review page$/) do
  step 'I visit your plea page with one charge against me'
  step 'I select not guilty to one charge'
  step 'I successfully fill out the not guilty form'
end

When(/^I see ([^\"]*) section header '([^\"]*)'$/) do |section, header|
  expect(review_page.send(section.to_sym).h2.text).to eq header
end

When(/^I see ([^\"]*) section header '([^\"]*)' with change ([^\"]*) link$/) do |section, header, link|
  expect(review_page.send(section.to_sym).h2.text).to eq header
  expect(review_page.send(section.to_sym).change_link['href']).to end_with link
end

When(/^I check confirmation$/) do
  review_page.form_group_wide.id_understand.set true
  review_page.button_large.click
end

Then(/^the ([^\"]*) section should have <title> <information> with link <change>$/) do |section, your_plea_details|
  your_plea_details.rows.each_with_index do |row, index|
    row[1] = (Date.today - 10).strftime('%d/%m/%Y') if row[1] == 'review_posting_date'
    expect(review_page.send(section.to_sym).dt[index].text).to start_with row[0]
    expect(review_page.send(section.to_sym).dd[index].text).to eq row[1]
    expect(review_page.send(section.to_sym).change_link_dl[index]['href']).to end_with row[2] unless row[2].empty?
  end
end

Then(/^the ([^\"]*) section should have <title> <information> without change links$/) do |section, your_plea_details|
  your_plea_details.rows.each_with_index do |row, index|
    expect(review_page.send(section.to_sym).dt[index].text).to start_with row[0]
    expect(review_page.send(section.to_sym).dd[index].text).to eq row[1]
  end
end

Then(/^your plea charge 1 should have plea\/1 link$/) do
  expect(review_page.your_plea.change_link['href']).to end_with '/plea/plea/1'
end

Then(/^I should see important notice with checkbox$/) do
  expect(review_page.form_group_wide.h2.text).to eq 'Important'
  expect(review_page.form_group_wide.important.text).to start_with 'It is an offence to make a false statement'
  expect(review_page.form_group_wide.id_understand['type']).to eq 'checkbox'
  expect(review_page.form_group_wide.checkbox_text.text).to start_with 'I confirm that I have read and understand'
end

When(/^I click on make your plea button$/) do
  review_page.button_large.click
end
