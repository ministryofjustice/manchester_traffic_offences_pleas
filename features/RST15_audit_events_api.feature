Feature: Creating Audit events is possible from outside the application 

    Background:

        Given fixtures from "auditevent_valid_exercise_api" are loaded
	And fixtures from "auditevent_create_api" are available
        And I am logged into the api interface as "apiuser"
        And I am logged into the admin interface as "servicemanager"

    Scenario Outline: A pre-processing step reports failing to process a case

        When an api call is made to create a "audit event" with pk "pk"
	Then the response is "success"

        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "event type"
        And the "audit event" field "event_subtype" has the value "event subtype"
	And the "audit event" field "case" is not present
		
        When I visit "/admin/auditevents/1"
	Then I see the details of the "auditevent" with pk "pk"

	Examples:
	    | id | event type     | event subtype | notes         |
	    | 1  | auditevent_api | EXT1          | basic failure |
	    | 2  | auditevent_api | EXT1          | basic failure |
	    | 3  | auditevent_api | EXT1          | basic failure |

    Scenario Outline: A valid case is presented to the API 

        When an api call is made to create a "case" with pk "pk"
	Then the response is "success"
	And the "case" is saved

        And the "audit event" is saved
        And the "audit event" field "event_type" has the value "case_api"
	And the "audit event" field "event_subtype" has the value "success"
	
	#Scenario: The service manager sees the case

	When I visit the "case" with pk "pk"
	Then I see the details of the "case" with pk "pk"

	#Scenario: The service manager sees the audit event
	
	When I visit the "audit event" with pk "pk"
	Then I see the details of the "audit event" with pk "pk"

	Examples:
	    | pk | urn           | event type | notes         |
	    | 1  | 53/23/0983738 | success    | basic success |
	    | 2  | 88/6G/8975433 | success    | basic success |
	    | 3  | 00/51/0000000 | success    | basic success |
	    | 4  | 07/55/8769098 | success    | basic success |
	
