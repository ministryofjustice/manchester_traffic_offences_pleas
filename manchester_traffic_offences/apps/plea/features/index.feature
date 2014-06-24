Feature: Fill out the plea form and review my information
    Scenario: Enter plea
        Given I access the url "/plea/about/?next=review"
        And I fill in "about-date_of_hearing_0" with "01/01/1977"
        And I fill in "about-date_of_hearing_1" with "18:00"
        And I fill in "about-urn" with "asd"
        And I fill in "about-name" with "asd"
        And I press continue
        And I choose "guilty" from "plea-guilty"
        And I fill in "plea-mitigations" with "asd"
        And I check "plea-understand"
        And I press continue
        Then I should see the text "Confirm"
        