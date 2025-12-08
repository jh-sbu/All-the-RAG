from dataclasses import dataclass
from typing import Optional


@dataclass
class Claims:
    iss: str
    sub: str


@dataclass
class AuthContext:
    _protected_claims: Optional[Claims]

    @property
    def logged_in(self) -> bool:
        return self._protected_claims is not None

    @property
    def claims(self) -> Claims:
        if self._protected_claims is None:
            raise ValueError("Not authenticated")
        return self._protected_claims

