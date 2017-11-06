Feature: Company details

  Background:
    Given I have validated a company URN

  Scenario: Submit details
    When I enter my name and contact details
    And I confirm my address as correct
    And I enter my company information
    And I press "Continue"
    Then I should be given a chance to plea to the first charge

  Scenario: Ask for correct address
    When I chose my address is incorrect
    Then I should see "If no, tell us the correct company address here"
