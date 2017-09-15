Feature: Your case, enter urn

  Background: Navigating to the enter urn page
    Given I visit the enter urn page

  Scenario: Displays header
    Then I should see 'Your case' header

  Scenario: Displays URN hint
    Then I should see provide URN hint

  Scenario: Valid URN
    When I enter a valid URN
    Then I am taken to notice_type/  

  Scenario: Date of birth and postcode are known
    When my date of birth and postcode are known
    Then I am taken to your_case_continued/  

  Scenario: Invalid URN returns error message
    When I enter an invalid URN
    Then I should see error message 'The Unique Reference Number (URN) isn't valid.' with link section_urn

  Scenario: Entering invalid URN multiple times
    When I enter an invalid URN three times
    Then I should see make a plea by post error message

  Scenario: Date of birth and postcode are known
    When my date of birth and postcode are known
    Then I am taken to your_case_continued/
