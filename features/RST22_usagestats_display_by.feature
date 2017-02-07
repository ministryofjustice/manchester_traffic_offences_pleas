Feature: Usage stats help to direct support efforts

    Background:
	
        Given I am logged into the admin interface as "servicemanager"

    Scenario: Usage stats can be displayed by court centre
	
	When I visit "/admin/plea/usagestats/?period=weekly"
	Then I see pleas grouped by court centre

    Scenario: Usage stats can be listed by month

	# This is difficult, especially for historic data without heroics. 
	# 4-weekly windows could be simple enough
	When I visit "/admin/plea/usagestats/?period=fourweekly/"
	Then I see stats grouped into 4 week entries
	And I see pleas grouped by court centre

    Scenario: Access to usage stats should be simple

	When I visit "/admin/plea/usagestats"
	Then I see a link to the weekly stats
	And I see a link to the monthly stats
