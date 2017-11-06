Feature: Personal details

  Background:
    Given I have validated a personal URN

  Scenario: Submit details without optional information
    When I enter my name and contact details
    And I confirm my address as correct
    And I don't provide National Insurance number
    And I don't provide UK driving licence number
    And I press "Continue"
    Then I should be given a chance to plea to the first charge

  Scenario: Ask for additional information and correct address
    When I choose to provide National Insurance number
    Then I should see "If yes, enter it here. It can be found on your National Insurance card, benefit letter"
    When I choose to provide UK driving licence
    Then I should see "If yes, enter it here. Your driving licence number is in section 5"
    When I chose my address is incorrect
    Then I should see "If no, tell us your correct address here"
