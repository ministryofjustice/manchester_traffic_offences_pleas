Feature: Handles welsh pleas for english courts

  Background: Visit make a plea
    When I visit "/plea/enter_urn/"
    And I press "Cymraeg"

  Scenario: Valid welsh urn should work
    When I submit a valid welsh URN in welsh
    Then I should see "Eich achos - parhad"
    And I should see "English"

  Scenario: Valid english urn shouldn't work
    When I submit a valid english URN in welsh
    Then I should see "Yn anffodus, nid yw’r cyfeirnod unigryw yn ddilys, ac nid yw’r system yn ei adnabod. Gallwch bledio yn Gymraeg os cyflawnwyd y drosedd yng Nghymru yn unig"