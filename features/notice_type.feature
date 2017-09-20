Feature: Notice type

  Background: Navigating to notice type page
    Given I visit the notice type page

  Scenario: Displays header
    Then I should see 'Your notice' header

  Scenario: Displays second header 
    Then I should see second header 'From page 1 of the notice we sent to you:'

  Scenario: Displays what is the title label
    Then I should see what is the title label

  Scenario: Displays help image
    Then I should see the help image

  Scenario: Selecting Single Justice Procedure Notice
    When I select Single Justice Procedure Notice
    Then I am taken to case/

  Scenario: Selecting Something else
    When I select Something else
    Then I am taken to case/
