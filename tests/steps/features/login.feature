Feature: User login
  As a registered user
  I want to log into the system
  So that I can access my private data

  Scenario: Login with valid credentials
    Given a registered user "alice@example.com" with password "Secret123!"
    When she logs in with email "alice@example.com" and password "Secret123!"
    Then the login should be successful
    And she should receive a session token

  Scenario: Login with wrong password
    Given a registered user "alice@example.com" with password "Secret123!"
    When she logs in with email "alice@example.com" and password "WrongPass"
    Then the login should be rejected
    And the error message should be "Invalid email or password"

  Scenario: Login with too many failed attempts
    Given a registered user "bob@example.com" with password "Secret123!"
    When he fails to log in 5 times with a wrong password
    Then his account should be temporarily locked
