@auth
Feature: Authentication
  As a registered shopper
  I want to sign in securely
  So that only valid accounts can reach the store

  Background:
    Given the shopper is on the login page

  @smoke
  Scenario: Standard user signs in successfully
    When the shopper signs in with username "standard_user" and password "secret_sauce"
    Then the product catalogue is displayed

  @negative @regression
  Scenario Outline: Sign-in is rejected with a clear message
    When the shopper signs in with username "<username>" and password "<password>"
    Then the login error "<message>" is shown
    And the shopper stays on the login page

    Examples:
      | username        | password       | message                                                                   |
      | locked_out_user | secret_sauce   | Epic sadface: Sorry, this user has been locked out.                       |
      | standard_user   | wrong_password | Epic sadface: Username and password do not match any user in this service |
      |                 | secret_sauce   | Epic sadface: Username is required                                        |
      | standard_user   |                | Epic sadface: Password is required                                        |

  @regression
  Scenario: Signed-in shopper can log out
    When the shopper signs in with username "standard_user" and password "secret_sauce"
    And the shopper logs out
    Then the shopper stays on the login page
