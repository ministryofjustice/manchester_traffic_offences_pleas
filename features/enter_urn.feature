Feature: Your case, enter urn

  Background: Navigating to the enter urn page
    Given I visit the enter urn page

  Scenario: Displays header
    Then I should see 'Your case' header

  Scenario: Displays URN hint
    Then I should see provide URN hint

  Scenario: Invalid URN returns error message
    When I enter an invalid URN
    Then I should see URN error message
    And I should see link to return to the input field

  Scenario: Displays make a plea by post error message
    When I enter an invalid URN three times
    Then I should see make a plea by post error message

  Scenario: Entering a valid URN
    When I enter a valid URN
    Then I am taken to the your case continued page


    