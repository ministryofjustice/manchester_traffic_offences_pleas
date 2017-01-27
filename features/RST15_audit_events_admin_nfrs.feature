Feature: Admin interface non-functional requirements

    Scenario: Audit events are visible to service managers

        Given I am logged into the admin interface as "service manager"
        When I visit "/admin/auditevents"
        Then I see the admin interface for "audit events"

    Scenario: Audit events are not visible when logged out

        Given I am logged out of the admin interface
        When I visit "/admin/auditevents"
        Then I see the admin login form

    Scenario: Audit events are not visible to court staff

        Given I am logged into the admin interface as "court staff"
        When I visit "/admin/auditevents"
        Then I see the admin login form
