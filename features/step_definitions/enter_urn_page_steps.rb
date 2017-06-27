Given(/^I visit the enter urn page$/) do
  enter_urn_page.load_page
end

When(/^I enter an invalid URN$/) do
  enter_urn_page.section_urn.urn_field.set('faoan')
  enter_urn_page.continue_button.click
end

Then(/^I should see your case page header$/) do
  expect(enter_urn_page.page_header.text).to eq 'Your case'
end

Then(/^I should see provide URN hint$/) do
  expect(enter_urn_page.section_urn).to have_text
  expect(enter_urn_page.section_urn).to have_hint
end

Then(/^I should see error message$/) do
  expect(enter_urn_page).to have_error_summary
end

Then(/^I should see link to return to the input field$/) do
  expect(current_path.enter_urn_page.error_summary.link['href'])
    .to end_with('#section_urn')
end
