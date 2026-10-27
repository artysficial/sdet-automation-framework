@catalog
Feature: Consistent behaviour across account types
  Every account type must get the same core shopping behaviour.

  @regression @known_defect
  Scenario: Sorting works for the problem_user account
    Given the shopper is signed in as "problem_user"
    When the shopper sorts products by "Name (Z to A)"
    Then the products are ordered by name descending
