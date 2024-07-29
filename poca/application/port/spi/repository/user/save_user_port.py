import decimal
from typing import Protocol


class SaveUserPort(Protocol):
    def save_user_balance(self, user_id: int, balance: decimal.Decimal) -> bool:
        """
        유저 잔액 저장
        :param user_id: int
        :param balance: decimal.Decimal
        :return: bool
        """
        raise NotImplementedError()
