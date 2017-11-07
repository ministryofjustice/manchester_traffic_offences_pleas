Feature: Your plea - validation

  Background: Navigating to your details page
    Given I visit your plea page with one charge against me

  Scenario: Displays you must select a plea for this charge error messages
    When I click on continue
    Then I should see error message 'You must select a plea for this charge' with link section_guilty

  Scenario: Displays you must tell us which language error messages  
    When I select yes to the guilty questions
    And I click on continue
    Then I should see error message 'You must tell us which language' with link section_sjp_interpreter_language
  
  Scenario: Displays all not guilty error messages
    When  I select not guilty to one charge
    And I click on continue
    Then I should see error <message> with <link>
    | message                            | link                           |
    | why you believe you are not guilty | section_not_guilty_extra       |
    | tell us if you need an interpreter | section_interpreter_needed     |
    | disagree with any of the evidence  | section_disagree_with_evidence |
    | you want to call a defence witness | section_witness_needed         |
  
  Scenario: Displays all not guilty further information error messages
    When I select yes to the not guilty questions
    And I click on continue
    Then I should see error <message> with <link>
    | message                            | link                                   |
    | why you believe you are not guilty | section_not_guilty_extra               |
    | You must tell us which language    | section_interpreter_language           |
    | tell us the name of the witness    | section_disagree_with_evidence_details |
    | name, address and date of birth    | section_witness_details                |
    | tell us which language             | section_witness_interpreter_language   |
    