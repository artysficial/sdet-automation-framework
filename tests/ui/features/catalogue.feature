@catalog
Feature: Product catalogue and cart
  As a shopper
  I want to browse, sort and select products
  So that I can build the basket I intend to buy

  Background:
    Given the shopper is signed in as "standard_user"

  @smoke
  Scenario: Catalogue lists every product with a valid price
    Then the catalogue shows 6 products
    And every product has a name and a positive price

  @regression
  Scenario Outline: Products can be sorted
    When the shopper sorts products by "<option>"
    Then the products are ordered by <field> <direction>

    Examples:
      | option              | field | direction  |
      | Name (A to Z)       | name  | ascending  |
      | Name (Z to A)       | name  | descending |
      | Price (low to high) | price | ascending  |
      | Price (high to low) | price | descending |

  @regression @cart
  Scenario: Cart badge tracks added and removed products
    When the shopper adds "Sauce Labs Backpack" to the cart
    And the shopper adds "Sauce Labs Bike Light" to the cart
    Then the cart badge shows 2
    When the shopper removes "Sauce Labs Backpack" from the cart
    Then the cart badge shows 1
