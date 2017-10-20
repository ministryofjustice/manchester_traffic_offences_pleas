Feature: Your details

  Background: Navigating to your details page
    Given I visit your details page

  Scenario: Displays header
    Then I should see 'Your details' header
    And I should see more information 'We need these in case we have to get in touch'

  Scenario: Displays name
    Then I should be asked for my first name
    And I should be asked for my last name

  Scenario: Displays address
    Then I should be asked if my address is correct

  Scenario: Displays contact number
    Then I should be asked for my contact number

  Scenario: Displays date of birth
    Then I should be asked for my date of birth

  Scenario: Displays email address
    Then I should be asked for my email address

  Scenario: My address is not correct
    When I fill out the form I click no my address is not correct
    And I enter my correct address
    Then I am taken to /plea/plea/1  

  Scenario: I have a National Insurance number
    When I click yes I have a National Insurance number
    And I enter my National Insurance number
    Then I am taken to /plea/plea/1

  Scenario: I have a UK driving license
    When I click yes I have a UK driving license
    And I enter my UK driving license number
    Then I am taken to /plea/plea/1

  Scenario: Successfully submits your details form
    When I successfully submit my details
    Then I am taken to /plea/plea/1

  Scenario: Displays error messages
    And I click on continue
    Then I should see error <message> with <link>
    | message                                         | link                        |
    | Enter your first name                           | section_first_name          |
    | Enter your last name                            | section_last_name           |
    | You must tell us if the address on the notice   | section_correct_address     |
    | You must provide a contact number               | section_contact_number      |
    | Tell us your date of birth                      | section_date_of_birth       |
    | You must provide an email address               | section_email               |
    | Tell us if you have a National Insurance number | section_have_ni_number      |
    | Tell us if you have a UK driving licence        | have_driving_licence_number |

  Scenario: Displays tell us your National Insurance number error message
    When I click yes I have a National Insurance number
    And I click on continue
    Then I should see error message 'Tell us your National Insurance number' with link section_ni_number

  Scenario: Displays tell us your driving licence number error message
    When I click yes I have a UK driving license
    And I click on continue
    Then I should see error message 'Tell us your driving licence number' with link section_driving_licence_number

  Scenario: Displays the date of birth must be before today
    When I fill out the form with a date of birth that is not before today
    Then I should see error message 'The date of birth must be before today' with link section_date_of_birth
  