Feature: Company details

  Background: Navigating to your details page
    Given I visit your company details page

   Scenario: Displays header
    Then I should see 'Your details' header

  Scenario: Displays we need these in case we have to contact you copy
    Then I should see we need these in case we have to contact you copy

  Scenario: Displays warning
    Then I should see warning

  Scenario: Displays company name
    Then I should be asked for the company name

  Scenario: Displays company's address
    Then I should be asked if the company address is correct

  Scenario: Displays name
    Then I should be asked your first name
    And I should be asked your last name

  Scenario: Displays position in company
    Then I should be asked my position in the company
    And I should be asked if I am the director
    And I should be asked if I am the company secretary   
    And I should be asked if I am the company solicitor

  Scenario: Displays contact number
    Then I should be asked for a contact number

  Scenario: Successfully submits company details form
    When I successfully submit the company details
    And I click on continue
    Then I am taken to /plea/plea/1

  Scenario: Displays error messages
    And I click on continue
    Then I should see error <message> with <link>
    | message                          | link                        |
    | Enter the company name           | section_company_name        |
    | Tell us if the company's address | section_correct_address     |
    | Enter your first name            | section_first_name          |
    | Enter your last name             | section_last_name           |
    | You must tell us your position   | section_position_in_company |
    | Enter a contact number           | section_contact_number      |
    