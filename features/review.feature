Feature: Review and submit a plea

  Background:
    Given I have validated a personal URN
    And I have submitted my personal information
    And I have pleaded guilty to both charges

  Scenario: Submit plea with confirmation
    Given I have entered my personal details
      | first_name | last_name | email           | contact_number |
      | John       | Doe       | john.doe@example.com| 1234567890     |
    And I have submitted my employment details
    When I confirm and submit my plea
    Then my details should match
    And I should receive the confirmation email

  @local
  Scenario: Confirmation and court emails sent
    When I confirm and submit my plea
    Then I should receive the confirmation email
    And the court should receive my plea email with attached details
    And police should receive confirmation email
