Feature: Your plea - Guilty
    
  Scenario: Guilty - I want to attend court in person
    Given I visit your plea page with one charge against me
    When I select guilty - I want to attend court in person
    And I successfully fill out the guilty form
    Then I am taken to /plea/your_status/

  Scenario: Pleading guilty on multiple charges
    Given I visit your plea page with three charges against me
    When I select guilty - I want to attend court in person
    And I successfully fill out the guilty form
    Then I am taken to /plea/plea/2

  Scenario: Guilty - I want the case to be dealt with in my absence
    Given I visit your plea page with one charge against me
    When I select guilty - I want the case to be dealt with in my absence
    And I click on continue
    Then I am taken to /plea/your_status/
  
  Scenario: Displays do you need an interpreter in court
    Given I visit your plea page with one charge against me
    When I select guilty - I want to attend court in person
    Then I should see do you need an interpreter in court

  Scenario: Displays tell us which language copy
    Given I visit your plea page with one charge against me
    When I select guilty - I want to attend court in person
    Then I should see tell us which language copy

  Scenario: Displays mitigation for guilty
    Given I visit your plea page with one charge against me
    When I select guilty - I want to attend court in person
    Then I should see mitigation for guilty
