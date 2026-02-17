# Language: Python 3.11
# Packages: pytest==9.0.2, pytest-bdd==7.2.0

from __future__ import annotations
from typing import Dict, Any

import pytest
from app.auth import AuthService


@pytest.fixture(scope="session")
def auth_service() -> AuthService:
    # 面試時可以說：實務上會改成呼叫 API / test DB
    return AuthService(max_failed_attempts=5)


@pytest.fixture
def context() -> Dict[str, Any]:
    # 存放目前 Scenario 的狀態（最後一次 response 等）
    return {}
