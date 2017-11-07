Feature: Company plea

  Background: Navigating to the company plea page
    Given I visit the company plea page

  Scenario: Displays header
    Then I should see 'Company plea' header

  Scenario: Displays present the company's case copy
    Then I should see present the company's case copy

  Scenario: Dispalys not guilty to this charge means copy
    When  I select not guilty to one charge
    Then I should see pleading not guilty to this charge means copy

  Scenario: Displays tell us why you believe the company is not label
    When I select not guilty to one charge
    Then I should see tell us why you believe the company is not guilty label

  Scenario: Displays does your company representative need an interpreter in court
    When I select not guilty to one charge
    Then I should see does your company representative need an interpreter in court

  Scenario: Successfully filling out form as guilty plea
    When I select guilty to one charge
    And I successfully fill out the guilty form
    Then I am taken to /plea/company_finances/

  Scenario: Successfully filling out form as not guilty plea
    When I select not guilty to one charge
    And I successfully fill out the not guilty form
    Then I am taken to /plea/review/
