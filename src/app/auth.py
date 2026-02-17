# Language: Python 3.11
# Packages: (none)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class User:
    email: str
    password: str
    is_locked: bool = False
    failed_attempts: int = 0


class AuthService:
    def __init__(self, max_failed_attempts: int = 5) -> None:
        self._users: Dict[str, User] = {}
        self._max_failed_attempts = max_failed_attempts

    def register(self, email: str, password: str) -> User:
        user = User(email=email, password=password)
        self._users[email] = user
        return user

    def login(self, email: str, password: str) -> Dict[str, str]:
        user = self._users.get(email)
        # 不洩漏帳號是否存在
        if user is None:
            return {"ok": False, "error": "Invalid email or password"}

        if user.is_locked:
            return {"ok": False, "error": "Account locked"}

        if password != user.password:
            user.failed_attempts += 1
            if user.failed_attempts >= self._max_failed_attempts:
                user.is_locked = True
                return {"ok": False, "error": "Account locked"}
            return {"ok": False, "error": "Invalid email or password"}

        user.failed_attempts = 0
        return {"ok": True, "token": "dummy-session-token"}
