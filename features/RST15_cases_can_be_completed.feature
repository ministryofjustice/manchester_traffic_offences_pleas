Feature: User journies for all outstanding cases can be completed

    Background:
	Given fixtures from "sanitised_prod_data" are available 
	And fixtures from "bdd_auth" are available
	And fixtures from "sanitised_prod_data" are loaded 
	
    Scenario:
	When I complete all outstanding user plea journies
	Then I see "Thank you for pleading" at the end of each journey
