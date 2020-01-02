Feature: Review and submit a plea

  Background:
    Given I have validated a personal URN
    And I have submitted my personal information
    And I have pleaded guilty to both charges
    And I have submitted my employment details

  Scenario: Submit plea with confirmation
    # When I review my case
    Then my details should match
    When I confirm and submit my plea
    Then I should see the confirmation page

  @local
  Scenario: Confirmation and court emails sent
    When I confirm and submit my plea
    Then I should receive the confirmation email
    And the court should receive my plea email with attached details
    And police should receive confirmation email
