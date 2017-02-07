Feature: Admin interface non-functional requirements

    Scenario: Audit events are visible to service managers

        Given I am logged into the admin interface as "servicemanager"
        When I visit "/admin/plea/auditevent/"
        Then I see the admin interface for "audit event"

    Scenario: Audit events are not visible when logged out

        Given I am logged out of the admin interface
        When I visit "/admin/plea/auditevent/"
        Then I see the admin login form

    Scenario: Audit events are not visible to court staff

        Given I am logged into the admin interface as "courtstaff"
        When I visit "/admin/plea/auditevent/"
        Then I see the admin login form
