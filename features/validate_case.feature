Feature: Validate case with URN, offences, postcode and date of birth

  Background:
    When I visit "plea/enter_urn/"

  Scenario: Valid URN, date of birth and postcode is known
    When I submit a valid URN
    Then I should be asked to validate my date of birth

  Scenario: Only date of birth is known
    When I submit a valid URN where only date of birth is known
    Then I should be asked to validate my date of birth

  Scenario: Only postcode is known
    When I submit a valid URN where only postcode is known
    Then I should be asked to validate my postcode

  Scenario: Invalid URN format returns error message
    When I submit an invalid URN
    Then I should see "The Unique Reference Number (URN) isn't valid."

  Scenario: Inexistent URN returns error message
    When I submit an inexistent URN
    Then I should see "The Unique Reference Number (URN) isn't valid."

  Scenario: Entering invalid URN multiple times
    When I submit an invalid URN three times
    Then I should see "please submit your plea by post using the forms enclosed."

  Scenario: Can't plea where date of birth and postcode are not known
    When I submit a valid URN where date of birth and postcode are not known
    Then I should see "To make your plea, you need to complete the paper form sent to you by the police."

  Scenario: Verify number of offences and date of birth
    When I submit a valid URN where only date of birth is known
    And I submit 1 charge and correct date of birth
    Then I should be asked for my personal details

  Scenario: Verify number of offences and postcode
    When I submit a valid URN where only postcode is known
    And I submit 1 charge and correct postcode
    Then I should be asked for my personal details

  Scenario: Verify number of offences and postcode as a company
    When I submit a valid URN as company
    And I submit 1 charge and correct postcode
    Then I should be asked for my company details

  Scenario: Number of offences doesn't match
    When I submit a valid URN where only date of birth is known
    And I fill in "number_of_charges" with "9"
    And I fill in correct date of birth
    And I press "Continue"
    Then I should see "The information you've entered does not match our records."

  Scenario: Date of birth doesn't match
    When I submit a valid URN where only date of birth is known
    And I fill in "number_of_charges" with "1"
    And I fill in incorrect date of birth
    And I press "Continue"
    Then I should see "The information you've entered does not match our records."

  Scenario: Postcode doesn't match
    When I submit a valid URN where only postcode is known
    And I fill in "number_of_charges" with "1"
    And I fill in "postcode" with "C1 1XX"
    And I press "Continue"
    Then I should see "The information you've entered does not match our records."
