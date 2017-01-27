Feature: Audit events for invalid case imports are stored

    Scenario Outline: A case with a missing field fails to import 

        Given the "case" from file "case name"
        When the "case" is posted to the api
        Then the response is "failure"
        And the "case" is not saved
        
        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "import"
        And the "audit event" field "reason_for_failure" has the value "reason for failure"
        And the "audit event" stack trace is present
        And the "audit event" field "datetime" has the value "just now"
        And the "audit event" contains a hash of the details of the case 

        Examples:
            | case name                 | reason for failure        |
            | case_invalid_missing_urn  | case_invalid_missing_urn  |
            | case_invalid_missing_name | case_invalid_missing_name |

    Scenario Outline: A case with an invalid field fails to import

        Given the "case" from file "case name"
        When the "case" is posted to the api
        Then the response is "failure"
        And the "case" is not saved

        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "import"
        And the "audit event" field "reason_for_failure" has the value "reason for failure"
        # By stack trace, I am most keen to get validation error type
        And the "audit event" stack trace is present
        And the "audit event" field "datetime" has the value "just now"
        And the "audit event" contains a hash of the details of the case 
    
        Examples:
            | case name                  | reason for failure         |
            | case_invalid_bad_urn       | case_invalid_bad_urn       |
            | case_invalid_name_too_long | case_invalid_name_badchars |
            | case_invalid_offencecode   | case_invalid_offencecode   |
            | case_invalid_courtcode     | case_invalid_courtcode     |
            | case_invalid_not_in_whitelist | case_invalid_not_in_whitelist |
            | case_invalid_duplicate_offence | case_invalid_duplicate_offence |

