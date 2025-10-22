Feature: Security Insights dashboard

  As a stakeholder
  I want to see a tailored dashboard
  So that I can make decisions based on risk

  @smoke
  Scenario Outline: Load stakeholder dashboard and verify basic widgets
    Given the app is running
    When I open the "<view>" dashboard
    Then I see KPI tiles
    And I see charts
    And I see a populated top insights table

    Examples:
      | view        |
      | soc         |
      | exec        |
      | compliance  |
      | advisor     |
