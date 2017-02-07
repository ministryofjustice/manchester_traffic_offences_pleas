Feature: Audit events convey useful information via admin interface

    Background:

        Given fixtures from "auditevent_valid_excercise_ui" are loaded
        And I am logged into the admin interface as "servicemanager"

    Scenario: Audit entries can be listed

	When I visit "/admin/plea/auditevent/"
	Then I see a list of "audit event" items

    Scenario: Audit entries can be sorted by URNs

	When I visit "/admin/plea/auditevent/?o=1"
        Then I see the "audit events" list sorted by "URN"
    
    Scenario: Audit events can be filtered by no urn

        When I visit "/admin/plea/auditevent/?urn=123"
	Then I see the "audit events" list filtered by "URN" = "123"
    
    Scenario: There is no case displayed inline if not imported

        When I visit "/admin/plea/auditevent/3/"
        Then I see the details of the "auditevent" with pk "3"
        And the "audit event" field "event_subtype" is present
        And I see no related "case"

    Scenario: The related case is displayed inline if imported 

        When I visit "/admin/plea/auditevent/2/"
        Then I see the details of the "auditevent" with pk "2"
        And the "audit event" field "event_subtype" is not present 
        And I see the related "case" with pk "2"

    Scenario: Audit events are displayed inline with cases when they exist

        When I visit "/admin/plea/case/2/"
        Then I see the details of the "case" with pk "2"
        And I see the related "audit event" with pk "2"
        And I see the related "audit event" with pk "3"
	
    Scenario: Audit events are not displayed inline with cases when there are none
		
	When I visit "/admin/plea/case/1/"
        Then I see the details of the "case" with pk "1"
        And I see no related "audit event" 
	
    Scenario: Audit event entries can be searched for by urn

	When I visit "/admin/plea/auditevent/?q=123"
	Then I see a list of "audit event" items

    @skip
    Scenario: Audit event filters are limited to remain useful
	
	When
	Then

    @skip
    Scenario: Audit event entries can be filtered by type

	When
	Then

    @skip
    Scenario: Audit event entries can be filtered by time range

	When
	Then


