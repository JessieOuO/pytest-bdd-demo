# Language: Python 3.11
# Packages: pytest==9.0.2, pytest-bdd==7.2.0

from __future__ import annotations
from typing import Dict, Any

import pytest
from pytest_bdd import scenario, given, when, then, parsers
from app.auth import AuthService


@scenario("features/login.feature", "Login with valid credentials")
def test_login_success():
    """BDD: happy path login."""


@scenario("features/login.feature", "Login with wrong password")
def test_login_wrong_password():
    """BDD: wrong password."""


@scenario("features/login.feature", "Login with too many failed attempts")
def test_login_too_many_attempts():
    """BDD: lockout behavior."""


@given(
    parsers.parse('a registered user "{email}" with password "{password}"'),
    target_fixture="registered_user",
)
def registered_user(auth_service: AuthService, email: str, password: str) -> str:
    auth_service.register(email=email, password=password)
    return email


@when(
    parsers.parse('she logs in with email "{email}" and password "{password}"'),
    target_fixture="login_result",
)
@when(
    parsers.parse('he logs in with email "{email}" and password "{password}"'),
    target_fixture="login_result",
)
def login_once(
    auth_service: AuthService,
    context: Dict[str, Any],
    email: str,
    password: str,
) -> Dict[str, Any]:
    result = auth_service.login(email=email, password=password)
    context["last_result"] = result
    return result


@when(
    parsers.parse("he fails to log in {times:d} times with a wrong password"),
    target_fixture="login_result",
)
def login_many_failed(
    auth_service: AuthService,
    context: Dict[str, Any],
    registered_user: str,
    times: int,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for _ in range(times):
        result = auth_service.login(email=registered_user, password="WrongPass")
    context["last_result"] = result
    return result


@then("the login should be successful")
def then_login_success(context: Dict[str, Any]):
    result = context["last_result"]
    assert result["ok"] is True
    assert "token" in result


@then("she should receive a session token")
def then_has_token(context: Dict[str, Any]):
    result = context["last_result"]
    assert isinstance(result.get("token"), str)


@then("the login should be rejected")
def then_login_rejected(context: Dict[str, Any]):
    result = context["last_result"]
    assert result["ok"] is False
    assert result["error"] in {"Invalid email or password", "Account locked"}


@then(parsers.parse('the error message should be "{message}"'))
def then_error_message(context: Dict[str, Any], message: str):
    result = context["last_result"]
    assert result["error"] == message


@then("his account should be temporarily locked")
def then_account_locked(context: Dict[str, Any]):
    result = context["last_result"]
    assert result["error"] == "Account locked"
