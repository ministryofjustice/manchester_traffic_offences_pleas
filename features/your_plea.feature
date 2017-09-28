Feature: Your plea - Generic

  Background: Navigating to your details page
    Given I visit your plea page

  Scenario: Displays header
    When I have one charge against me
    Then I should see 'Your plea' header

  Scenario: Displays present your case copy
    When I have one charge against me
    Then I should see present your case copy

  Scenario: Displays charge number header for one charge
    When I have one charge against me
    Then I should see second header 'Charge 1 of 1'

  Scenario: Displays charge number header for multiple charges
    When I have three charges against me
    Then I should see second header 'Charge 1 of 3'

  Scenario: Displays plea options
    When I have one charge against me
    Then I should see plea options
