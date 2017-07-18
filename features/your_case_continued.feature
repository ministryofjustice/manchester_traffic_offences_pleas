Feature: Your case continued

  Background: Navigating to the your case continued
    Given I visit the your case continued page

  Scenario: Displays header
    And my date of birth is known
    Then I should see 'Your case continued' header

  Scenario: Displays number of offences
    When my date of birth is known
    Then I should see number of offences label
    And I should see number of offences hint

  Scenario: Displays date of birth
    When my date of birth is known
    Then I should see date of birth label

  Scenario: Displays postcode
    When my date of birth is not known
    Then I should see postcode label
    And I should see postcode hint

  Scenario: Does not display postcode
    And my date of birth is known
    Then I should not see postcode

  Scenario: Does not display date of birth
    And my date of birth is not known
    Then I should not see date of birth

  Scenario: Successfully filling out form with date of birth
    And my date of birth is known
    When I enter 1 into the number of offences input field
    And I enter a valid date of birth
    Then I should be taken to your details page

  Scenario: Successfully filling out form with postcode
    And my date of birth is not known
    When I enter 1 into the number of offences input field
    And I enter C1 1CC as the postcode
    Then I should be taken to your details page

  Scenario: Displays error messages
    And my date of birth is known
    When I click on continue
    Then I should see error message 'Enter the number of charges against you'
    And I should see second error message 'Tell us your date of birth'

  Scenario: Displays enter a whole number error message
    And my date of birth is known
    When I enter a into the number of offences input field
    And I click on continue
    Then I should see error message 'Enter a whole number.'

  Scenario: Displays value is less than or equal to 10 error message
    And my date of birth is known
    When I enter 60 into the number of offences input field
    And I click on continue
    Then I should see error message 'Ensure this value is less than or equal to 10.'

  Scenario: Displays check the details you've entered error message
    And my date of birth is not known
    When I enter 1 into the number of offences input field
    And I enter C1 1AC as the postcode
    Then I should see check the details you've entered error message

  Scenario: Displays enter your postcode error message
    And my date of birth is not known
    When I enter 1 into the number of offences input field
    And I click on continue
    Then I should see error message 'Enter your postcode'
