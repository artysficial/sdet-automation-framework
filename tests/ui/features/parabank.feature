@banking
Feature: ParaBank online banking
  As a bank customer
  I want to sign in and move money between my accounts
  So that I can manage my finances online

  Background:
    Given the customer is on the ParaBank login page

  @smoke
  Scenario: Customer signs in and sees their accounts
    When the customer signs in with valid credentials
    Then the accounts overview is displayed
    And at least one account is listed

  @regression
  Scenario: Customer transfers funds between accounts
    When the customer signs in with valid credentials
    And the customer transfers "50.00" between two accounts
    Then the transfer is confirmed
