Feature: Plea to charges

  Background:
    Given I have validated a personal URN
    And I have submitted my personal information

  Scenario: Plea guilty to both charges, don't attend, no mitigation
    When I plea guilty, and choose not to attend court
    Then I should see "Charge 2 of 2"
    When I plea guilty, and choose not to attend court
    Then I should be asked for my employment status

  Scenario: Ask for additional information
    When I choose guilty - don't attend
    Then I should see "Is there something you would like the court to consider?"
    When I choose guilty - attend
    Then I should see "Do you need an interpreter in court?"
    Then I should not see "If there is a hearing, which language do you wish to speak?"
    Then I should not see "Please state in which language you wish to receive any further documentation?"
    When I choose not guilty
    Then I should see "Do you disagree with any evidence from a witness statement in the notice we sent to you?"
    Then I should see "Do you want to call a defence witness?"
    Then I should not see "If there is a hearing, which language do you wish to speak?"
    Then I should not see "Please state in which language you wish to receive any further documentation?"
