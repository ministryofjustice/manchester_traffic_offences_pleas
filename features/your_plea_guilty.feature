Feature: Your plea - Guilty

  Background: Navigating to your details page
    Given I visit your plea page
    
  Scenario: Successfully filling out form as guilty plea
    When I select guilty to one charge
    And I successfully fill out the guilty form
    Then I am taken to /plea/your_status/

  Scenario: Displays do you want to come to court to plead guilty
    When I select guilty to one charge
    Then I should see do you want to come to court to plead guilty

  Scenario: Displays do you need an interpreter in court
    When I select guilty to one charge
    Then I should see do you need an interpreter in court

  Scenario: Displays tell us which language copy
    When I select guilty to one charge
    Then I should see tell us which language copy

  Scenario: Displays mitigation for guilty
    When I select guilty to one charge
    Then I should see mitigation for guilty

  Scenario: Pleading guilty on multiple charges
    When I select guilty to three charges
    And I successfully fill out the guilty form
    Then I am taken to /plea/plea/2
