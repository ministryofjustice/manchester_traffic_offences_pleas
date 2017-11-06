Feature: Access the website in English and Welsh

  Background: Visit make a plea
    When I visit "/"

  Scenario: Switch between languages
    When I press "Cymraeg"
    Then I should see "Cofnodi ple ar-lein"
    When I press "English"
    Then I should see "Make a plea online"

  Scenario: Further pages load in selected language
    When I press "Cymraeg"
    And I press "Dechrau nawr"
    Then I should see "Beth yw eich Cyfeirnod unigryw (URN)?"
