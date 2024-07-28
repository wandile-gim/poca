import uuid
from typing import Protocol

from poca.application.domain.model.user import UserDomain


class FindUserPort(Protocol):
    def get_user_by_user_email(self, email: str) -> UserDomain:
        raise NotImplementedError()

    def get_user_by_user_id(self, user_id: int) -> UserDomain:
        raise NotImplementedError()
