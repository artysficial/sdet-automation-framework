@checkout
Feature: Checkout and order pricing
  As a shopper
  I want an accurate order summary and a smooth checkout
  So that I pay exactly what I expect

  Background:
    Given the shopper is signed in as "standard_user"

  @smoke
  Scenario: Shopper completes an order end to end
    When the shopper adds "Sauce Labs Backpack" to the cart
    And the shopper adds "Sauce Labs Bolt T-Shirt" to the cart
    And the shopper checks out as "Rahmadani" "Ningrum" with postal code "12950"
    Then the order summary lists 2 items
    And the order total equals the item total plus 8% tax
    When the shopper confirms the order
    Then the confirmation "Thank you for your order!" is shown
    And the cart is empty

  @regression
  Scenario Outline: Order totals are calculated correctly for different baskets
    When the shopper adds the products "<products>" to the cart
    And the shopper checks out as "Test" "Shopper" with postal code "10110"
    Then the order summary lists <count> items
    And the order total equals the item total plus 8% tax

    Examples:
      | products                                                                                                                                                | count |
      | Sauce Labs Onesie                                                                                                                                       | 1     |
      | Sauce Labs Fleece Jacket, Sauce Labs Bike Light                                                                                                         | 2     |
      | Sauce Labs Backpack, Sauce Labs Bike Light, Sauce Labs Bolt T-Shirt, Sauce Labs Fleece Jacket, Sauce Labs Onesie, Test.allTheThings() T-Shirt (Red) | 6     |

  @regression @known_defect
  Scenario: Order amounts are displayed in dollars and cents
    When the shopper adds the products "Sauce Labs Fleece Jacket, Sauce Labs Bike Light" to the cart
    And the shopper checks out as "Test" "Shopper" with postal code "10110"
    Then every amount in the order summary is shown in dollars and cents

  @negative @regression
  Scenario Outline: Checkout requires complete customer details
    When the shopper adds "Sauce Labs Onesie" to the cart
    And the shopper checks out as "<first>" "<last>" with postal code "<postal>"
    Then the checkout error "<message>" is shown

    Examples:
      | first | last    | postal | message                        |
      |       | Ningrum | 12950  | Error: First Name is required  |
      | Dani  |         | 12950  | Error: Last Name is required   |
      | Dani  | Ningrum |        | Error: Postal Code is required |
