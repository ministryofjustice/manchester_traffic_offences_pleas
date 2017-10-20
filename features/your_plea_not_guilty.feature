Feature: Your plea - Not guilty

  Scenario: Successfully filling out form for not guilty
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    And I successfully fill out the not guilty form
    Then I am taken to plea/review/
    
  Scenario: Displays not guilty because copy
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    Then I should see not guilty because copy

  Scenario: Displays need an interpreter in court header
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    Then I should see do you need an interpreter in court header
    And it should display yes and no option an interpreter in court
    And yes should display tell us which language

  Scenario: Displays evidence and witness header
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    Then I should see evidence and witness header
   
  Scenario: Displays disagree with any evidence section
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    Then I should see do you disagree with any evidence section
    And it should display yes and no option for disagree with any evidence

  Scenario: Displays witness information
    Given I visit your plea page with one charge against me
    When I select not guilty to one charge
    Then I should see witness information

  Scenario: Pleading not guilty on three charges
    Given I visit your plea page with three charges against me
    When I select not guilty to three charges
    And I successfully fill out the not guilty form
    Then I am taken to /plea/plea/2
