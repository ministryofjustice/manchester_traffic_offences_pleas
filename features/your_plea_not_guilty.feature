Feature: Your plea - Not guilty

  Background: Navigating to your details page
    Given I visit your plea page

  Scenario: Successfully filling out form for not guilty
    When I select not guilty to one charge
    And I successfully fill out the not guilty form
    Then I am taken to plea/review/
    
  Scenario: Displays not guilty because copy
    When I select not guilty to one charge
    Then I should see not guilty because copy

  Scenario: Displays need an interpreter in court header
    When I select not guilty to one charge
    Then I should see do you need an interpreter in court header
    And it should display yes and no option an interpreter in court
    And yes should display tell us which language

  Scenario: Displays evidence and witness header
    When I select not guilty to one charge
    Then I should see evidence and witness header
   
  Scenario: Displays disagree with any evidence section
    When I select not guilty to one charge
    Then I should see do you disagree with any evidence section
    And it should display yes and no option for disagree with any evidence

  Scenario: Displays witness information
    When I select not guilty to one charge
    Then I should see witness information

  Scenario: Pleading not guilty on three charges
    When I select not guilty to three charges
    And I successfully fill out the not guilty form
    Then I am taken to /plea/plea/2
