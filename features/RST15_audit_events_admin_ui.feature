Feature: Audit events convey useful information via admin interface

    Background:

        Given the "case" from file "auditevent_valid_excercise_ui"
        Given I am logged into the admin interface as "service manager"
        
    Scenario: Audit entries can be filtered by URNs

        When I visit "/admin/auditevents?filter=urn"
        Then I see the "audit events" sorted by "urn"
    
    Scenario: Audit events can be filtered by no urn

        When I visit "/admin/auditevents?filter=urn"
        Then I see the "audit events" sorted by "urn"
    
    Scenario: There is no case displayed inline if not imported

        When I visit "/admin/auditevents/1"
        Then I see the details of the "auditevent" with pk "1"
        And the "audit event" field "reason_for_failure" is present
        And I see no related "case"

    Scenario: The related case is displayed inline if imported 

        When I visit "/admin/auditevents/2"
        Then I see the details of the "auditevent" with pk "2"
        And the "audit event" field "reason_for_failure" is not present 
        And I see the related "case" with pk "2"

    Scenario: Audit events are displayed inline with cases

        When I visit "/admin/case/2"
        Then I see the details of the "case" with pk "2"
        And I see the related "audit event" with pk "2"
        And I see the related "audit event" with pk "3"

