Feature: Make a Plea landing Page

  Background: Navigating to the make a plea landing page
    Given I visit the make a plea landing page

  Scenario: Displays header
    Then I should see page header

  Scenario: Displays get started intro
    Then I should see get started intro

  Scenario: Page also available in Welsh
    And I see available in Welsh copy
    When I click on the Welsh copy link
    Then I should see make a plea for a traffic offence in Welsh

  Scenario: Start now
    When I click on the start now button
    Then I should be taken to "Your case" page

  Scenario: Displays before you start copy
    Then I should see before you start copy

  Scenario: Link to contact the court
    Then I should see link to contact the court

  Scenario: Link to get help with making a plea online
    Then I should see link to get help with making a plea online


