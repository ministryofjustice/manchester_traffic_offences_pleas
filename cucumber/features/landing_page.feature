Feature: Make a Plea landing Page

  Background: Navigating to the make a plea landing page
    Given I visit the make a plea landing page

  Scenario: Displays content
    Then I should see page header

  Scenario: Start now
    When I click on the start now button
    Then I should be taken to your case page

