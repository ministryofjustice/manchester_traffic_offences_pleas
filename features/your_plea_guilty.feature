Feature: Your plea - Guilty
    
  Scenario: Successfully filling out form as guilty plea
    Given I visit your plea page with one charge against me
    When I successfully fill out the guilty form
    Then I am taken to /plea/your_status/

  Scenario: Displays do you want to come to court to plead guilty
    Given I visit your plea page with one charge against me
    Then I should see do you want to come to court to plead guilty

  Scenario: Displays do you need an interpreter in court
    Given I visit your plea page with one charge against me
    Then I should see do you need an interpreter in court

  Scenario: Displays tell us which language copy
    Given I visit your plea page with one charge against me
    Then I should see tell us which language copy

  Scenario: Displays mitigation for guilty
    Given I visit your plea page with one charge against me
    Then I should see mitigation for guilty

  Scenario: Pleading guilty on multiple charges
    Given I visit your plea page with three charges against me
    When I successfully fill out the guilty form
    Then I am taken to /plea/plea/2
