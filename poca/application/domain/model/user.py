import dataclasses
import decimal
import uuid


@dataclasses.dataclass
class UserDomain:
    user_id: uuid.UUID
    balance: decimal.Decimal
    email: str
    active: bool

    def is_user_can_purchase(self, price: decimal.Decimal) -> bool:
        return self.balance >= price
