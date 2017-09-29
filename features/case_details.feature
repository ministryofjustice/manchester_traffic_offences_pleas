Feature: Case details

  Background: Navigating to the case page
    Given I visit the case details page

  Scenario: Displays header
    Then I should see 'Case details' header

  Scenario: Displays posting date
    Then I should see posting date label
    And I should see posting date hint

  Scenario: Displays number of offences
    Then I should see offences label
    And I should see offences hint

  Scenario: Displays are you?
    Then I should see are you label
    And I should see are you hint

  Scenario: Displays help image
    Then I should see the help image

  Scenario: Displays provide a posting date error message
    When I fill out my case details without providing a date
    Then I should see error message 'Provide a posting date' with link section_posting_date
    But I should not see other error messages

  Scenario: Displays enter the number of charges error message
    When I fill out my case details without providing the number of charges
    Then I should see error message 'Enter the number of charges' with link section_number_of_charges
    But I should not see other error messages

  Scenario: Displays tell us if you are the person error message
    When I fill out my case details without selecting plea made by option
    Then I should see error message 'tell us if you are the person' with link section_plea_made_by
    And I should not see other error messages

  Scenario: The person named in the notice
    When I successfully fill out the form as the person named in the notice
    Then I am taken to your_details/

  Scenario: Pleading on the behalf of a company
    When I successfully fill out the form on the behalf of a company
    Then I am taken to company_details/
