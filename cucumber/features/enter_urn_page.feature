Feature: Your case, enter urn

  Background: Navigating to the enter urn page
    Given I visit the enter urn page

  Scenario: Displays header
    Then I should see your case page header

  Scenario: Asked to provide URN
    Then I should be asked to provide my URN number
    And I should see a hint

  Scenario: Invalid URN returns error message
    When I enter an invalid URN
    Then I should see error message
    And I should see link to return to the input field
    