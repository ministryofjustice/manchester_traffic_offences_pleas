Feature: Court finder

  Background:
    When I visit "/court-finder/"

  Scenario: Only enter 2 numbers correspond to valid court
    When I submit a valid court code
    Then I should see "You can contact the court by post or email quoting your URN before the date of your hearing."

  Scenario: Only enter 2 numbers correspond to invalid court
    When I submit an invalid court code
    Then I should see "We can't find your court"

  Scenario: Enter invalid URN, but with valid court code
    When I submit valid court code with invalid URN
    Then I should see "You can contact the court by post or email quoting your URN before the date of your hearing."

  Scenario: Enter valid URN
    When I submit a valid URN for court finder
    Then I should see "You can contact the court by post or email quoting your URN before the date of your hearing."

   Scenario: Enter invalid URN
    When I submit an invalid URN for court finder
    Then I should see "We can't find your court"