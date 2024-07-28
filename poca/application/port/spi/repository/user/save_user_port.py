import decimal
import uuid
from typing import Protocol


class SaveUserPort(Protocol):
    def save_user_balance(self, user_id: int, balance: decimal.Decimal) -> bool:
        raise NotImplementedError()
