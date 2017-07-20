Given(/^I visit the enter urn page$/) do
  enter_urn_page.load_page
end

When(/^I enter an invalid URN$/) do
  enter_urn_page.section_urn.urn_field.set('faoan')
  enter_urn_page.continue_button.click
end

When(/^I enter a valid URN$/) do
  enter_urn_page.section_urn.urn_field.set('51GH6735264')
  enter_urn_page.continue_button.click
end

When(/^I enter an invalid URN three times$/) do
  3.times do
    enter_urn_page.section_urn.urn_field.set('faoan')
    enter_urn_page.continue_button.click
  end
end

Then(/^I should see provide URN hint$/) do
  expect(enter_urn_page.section_urn).to have_text
  expect(enter_urn_page.section_urn).to have_hint
end

Then(/^I should see URN error message$/) do
  error = enter_urn_page.error_summary

  expect(error.h1[0].text).to eq 'You need to fix the errors on this page before continuing.'
  expect(error.p.count).to eq 1
  expect(error.link.text).to have_content 'The Unique Reference Number (URN) isn\'t valid. '
end

Then(/^I should see link to return to the input field$/) do
  expect(enter_urn_page.error_summary.link['href']).to end_with('#section_urn')
end

Then(/^I should see make a plea by post error message$/) do
  error = enter_urn_page.error_summary

  expect(error.h1[1].text).to eq 'Make a plea by post'
  expect(error.p.count).to eq 2
end

Then(/^I am taken to the your case continued page$/) do
  expect(current_path).to end_with '/plea/your_case_continued/'
end
