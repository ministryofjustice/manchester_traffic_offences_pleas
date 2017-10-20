Feature: Your plea - Generic

  Scenario: Displays header
    Given I visit your plea page with one charge against me
    Then I should see 'Your plea' header

  Scenario: Displays present your case copy
    Given I visit your plea page with one charge against me
    Then I should see present your case copy

  Scenario: Displays charge number header for one charge
    Given I visit your plea page with one charge against me
    Then I should see second header 'Charge 1 of 1'

  Scenario: Displays charge number header for multiple charges
    Given I visit your plea page with three charges against me
    Then I should see second header 'Charge 1 of 3'

  Scenario: Displays plea options
    Given I visit your plea page with one charge against me
    Then I should see plea options
