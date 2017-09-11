
Feature: Your case, enter urn

  Background: Navigating to the enter urn page
    Given I visit the enter urn page

  Scenario: Displays header
    Then I should see 'Your case' header

  Scenario: Displays URN hint
    Then I should see provide URN hint

  Scenario: Invalid URN returns error message
    When I enter an invalid URN
    Then I should see error message 'The Unique Reference Number (URN) isn't valid.'
    And I should see error link '#section_urn'

  Scenario: Displays make a plea by post error message
    When I enter an invalid URN three times
    Then I should see make a plea by post error message

  Scenario: Entering a valid URN
    When I enter a valid URN
    Then I am taken to /plea/notice_type/