Feature: Fill out employment status

  Background:
    Given I have validated a personal URN
    And I have submitted my personal information
    And I have pleaded guilty to both charges

  Scenario: Employed
    When I submit my employment status as "Employed"
    And I submit my home pay amount
    Then I should see my calculated weekly income of "923.08"
    When I choose no hardship
    And I press "Continue"
    Then I should see be asked to review my plea

  Scenario: Employed with benefits
    When I submit my employment status as "Employed and also receiving benefits"
    And I submit my home pay amount
    Then I should see "Which benefit do you receive?"
    When I submit my benefits as "Universal Credit"
    Then I should see my calculated weekly income of "1,384.62"
