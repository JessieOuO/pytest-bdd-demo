# Language: Python 3.11
# Packages: pytest==9.0.2, pytest-bdd==7.2.0, selenium==4.40.0

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import pytest
from pytest_bdd import scenario, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@dataclass
class LoginPage:
    driver: webdriver.Chrome
    base_url: str

    def open(self) -> None:
        self.driver.get(f"{self.base_url}/login")

    def enter_credentials(self, username: str, password: str) -> None:
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(password)

    def click_login(self) -> None:
        self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    def get_error_message(self) -> str:
        try:
            error = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message"))
            )
            return error.text
        except TimeoutException:
            return ""

    def is_login_button_disabled(self) -> bool:
        button = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        return button.get_attribute("disabled") == "true"


@pytest.fixture
def chrome_driver():
    """Headless Chrome for CI, non-headless for local debugging."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless=new")  # 面試時可以取消註解
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def login_page(chrome_driver, base_url: str) -> LoginPage:
    return LoginPage(driver=chrome_driver, base_url=base_url)


@pytest.fixture
def base_url() -> str:
    return "http://localhost:3000"  # 假設你的前端跑在這


@pytest.mark.ui
@pytest.mark.skip(reason="Requires web server running on localhost:3000")
@scenario("features/login_ui.feature", "Successful login via UI")
def test_ui_login_success():
    """UI BDD: happy path login."""


@pytest.mark.ui
@pytest.mark.skip(reason="Requires web server running on localhost:3000")
@scenario("features/login_ui.feature", "Lockout after multiple failed login attempts")
def test_ui_lockout():
    """UI BDD: brute-force protection."""


@pytest.mark.ui
@pytest.mark.skip(reason="Requires web server running on localhost:3000")
@scenario("features/login_ui.feature", "Permission denied for unauthorized page")
def test_ui_permission_denied():
    """UI BDD: unauthorized access."""


@given("I am on the login page")
def open_login(login_page: LoginPage):
    login_page.open()


@when(parsers.parse('I enter username "{username}" and password "{password}"'))
def enter_credentials(login_page: LoginPage, username: str, password: str):
    login_page.enter_credentials(username, password)


@when("I click the login button")
def click_login(login_page: LoginPage):
    login_page.click_login()


@when(
    parsers.parse('I enter username "{username}" and password "{password}" {times:d} times')
)
def enter_credentials_multiple(login_page: LoginPage, username: str, password: str, times: int):
    """Multiple failed attempts for lockout testing."""
    for _ in range(times):
        login_page.enter_credentials(username, password)
        login_page.click_login()
        # 避免過快，模擬真人打字
        import time
        time.sleep(0.5)


@when('I try to access "{path}" without login')
def access_protected_page(chrome_driver: webdriver.Chrome, base_url: str, path: str):
    chrome_driver.get(f"{base_url}{path}")


@then("I should see the user dashboard")
def verify_dashboard(login_page: LoginPage):
    WebDriverWait(login_page.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='dashboard']"))
    )


@then('I should see "{message}" error')
def verify_error_message(login_page: LoginPage, message: str):
    actual = login_page.get_error_message()
    assert message in actual


@then("the session should be authenticated")
def verify_authenticated(login_page: LoginPage):
    # 檢查 URL 或特定元素
    assert "/dashboard" in login_page.driver.current_url


@then("login should be disabled for 5 minutes")
def verify_login_disabled(login_page: LoginPage):
    assert login_page.is_login_button_disabled()


@then("I should be redirected to login page")
def verify_redirected_to_login(chrome_driver: webdriver.Chrome):
    assert "/login" in chrome_driver.current_url
