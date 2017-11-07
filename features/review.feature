Feature: Review - Confirm your plea

  Background: Navigating to the review page - confirm your plea
    Given I visit the review page

  Scenario: Displays header
    Then I should see 'Confirm your plea' header

  Scenario: Displays case details
    When I see case_details section header 'Case details'
    Then the case_details section should have <title> <information> with link <change>
    | title                   | information                 | change     |
    | Unique reference number | 98/FF/12345/84              | enter_urn/ |
    | Posting date            | review_posting_date         | case/      |
    | Number of offences      | 1                           |            |
    | You are                 | Person named on the notice  |            |          

  Scenario: Displays your details
    When I see your_details section header 'Your details' with change your_details/ link
    Then the your_details section should have <title> <information> without change links
    | title                     | information              |
    | First name                | John                     |
    | Middle name               | George                   |
    | Last name                 | Smith                    |
    | Address                   | As printed on the notice |
    | Contact number            | 0207514445               |          
    | Date of birth             | 07/03/1987               |
    | Email address             | test@hmcts.net           |
    | National Insurance number | -                        |
    | UK driving licence number | -                        |

  Scenario: Displays your plea
    When I see your_plea section header 'Your plea'
    Then your plea charge 1 should have plea/1 link
    And the your_plea section should have <title> <information> without change links
    | title                           | information                                       |
    | Your plea                       | Not guilty                                        |
    | Not guilty because              | I was not the driver                              |  
    | Interpreter required            | Yes                                               |
    | Language                        | German                                            |
    | Disagree with any evidence      | Yes                                               |       
    | Name of the witness             | Paul Smith was the driver                         |
    | Wants to call a witness?        | Yes                                               |
    | Name, date of birth and address | Paul Smith, 102 Petty France, London. 07777111222 |
    | Interpreter required            | Yes                                               |
    | Language                        | German                                            |

  Scenario: Displays important
    Then I should see important notice with checkbox

  Scenario: Displays error message
    When I click on make your plea button
    Then I should see error message 'You must confirm that you have read' with link section_understand

  Scenario: Successfully submit review plea page
    When I check confirmation
    Then I am taken to plea/complete/
