import dataclasses
import decimal
import uuid


@dataclasses.dataclass
class UserDomain:
    user_id: int
    balance: decimal.Decimal
    email: str
    active: bool

    def is_user_can_purchase(self, price: decimal.Decimal) -> bool:
        return self.balance >= price

    def buy_photo_card(self, price: decimal.Decimal):
        self.balance -= price
        return self
