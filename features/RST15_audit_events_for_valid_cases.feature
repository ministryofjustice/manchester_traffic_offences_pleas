Feature: Audit events for valid case imports are stored

    Scenario Outline: A case with valid, minimal fields is imported

        Given fixtures from "case_valid_minimal" are available
	When the "case" is posted to the api
	Then the response is "success"

        And the "case" is saved
        And the "case" field "court code" is present
        And the "case" field "offence code" is present
        And the "case" field "URN" is present
        
        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "import"
        And the "audit event" field "datetime" has the value "just now"
	And the "audit event" field "case" has the value "case_pk"

	Examples:
            |||

    Scenario Outline: A case with valid fields and optional ones is imported

        Given fixtures from "case_valid_extra" are available
        When the "case" is posted to the api
        Then the response is "success" 
        And the "case" is saved
        
        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "import"
        And the "audit event" field "datetime" has the value "just now"
        And the "audit event" field "case" has the value "case_pk"

	Examples:
	    |||
