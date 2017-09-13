Given(/^I visit the enter urn page$/) do
  enter_urn_page.load_page
end

When(/^I enter an invalid URN$/) do
  enter_urn_page.section_urn.urn_field.set URN[:invalid]
  enter_urn_page.continue_button.click
end

When(/^my date of birth and postcode are known$/) do
  enter_urn_page.section_urn.urn_field.set URN[:dob_postcode_known]
  enter_urn_page.continue_button.click
end

When(/^I enter a valid URN$/) do
  enter_urn_page.section_urn.urn_field.set URN[:valid]
  enter_urn_page.continue_button.click
end

When(/^I enter an invalid URN three times$/) do
  3.times do
    enter_urn_page.section_urn.urn_field.set URN[:invalid]
    enter_urn_page.continue_button.click
  end
end

Then(/^I should see provide URN hint$/) do
  expect(enter_urn_page.section_urn).to have_text
  expect(enter_urn_page.section_urn).to have_hint
end
