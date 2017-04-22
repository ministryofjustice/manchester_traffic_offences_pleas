Feature: Make a Plea landing Page

  Background: Navigating to the make a plea landing page
    Given I visit the make a plea landing page

  Scenario: Displays content
    Then I should see page header
    And I should see get started intro

  Scenario: Page also available in Welsh
    And I should see available in Welsh copy
    When I click on the Welsh copy link
    Then I should see


  Scenario: Start now
    When I click on the start now button
    Then I should be taken to "Your case" page

