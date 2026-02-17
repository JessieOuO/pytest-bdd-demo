Feature: Login UI with security scenarios
  As a security-conscious user
  I want to log in through the web interface
  So that I can access protected features safely

  Scenario: Successful login via UI
    Given I am on the login page
    When I enter username "demo" and password "demo"
    And I click the login button
    Then I should see the user dashboard
    And the session should be authenticated

  Scenario: Lockout after multiple failed login attempts
    Given I am on the login page
    When I enter username "demo" and password "wrong" 5 times
    Then I should see "Account temporarily locked" error
    And login should be disabled for 5 minutes

  Scenario: Permission denied for unauthorized page
    Given I am on the login page
    When I try to access "/admin" without login
    Then I should be redirected to login page
