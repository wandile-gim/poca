import dataclasses
import decimal
import enum
from decimal import Decimal

from poca.application.domain.model.user import UserDomain


class OnSaleQueryStrategy(enum.Enum):
    MIN_PRICE_RENEWAL_LATE_FIRST = "MIN_PRICE_RENEWAL_LATE_FIRST"


class PhotoCardState(enum.Enum):
    ON_SALE = "판매중"
    SOLD = "판매완료"


class FeePolicy:

    def __init__(self, discount_percentage: Decimal):
        self.discount_percentage = discount_percentage

    def apply(self, price):
        fee = price * (self.discount_percentage / Decimal('100'))
        return decimal.Decimal(fee)


@dataclasses.dataclass
class PhotoCard:
    id: int
    name: str
    description: str
    release_date: str
    image_url: str = ""

    def __str__(self):
        return f'Id:{self.id} | 카드 이름: {self.name}'


@dataclasses.dataclass
class PhotoCardSale:
    state: PhotoCardState
    price: decimal.Decimal
    fee: decimal.Decimal
    renewal_date: str
    version: int = 0
    id: int = None
    sold_date: str = None
    photo_card: PhotoCard = None
    seller: UserDomain = None
    buyer: UserDomain = None
    create_date: str = None
    _total_price: decimal.Decimal = None
    photo_card_id: int = None
    buyer_id: int = None
    seller_id: int = None

    def is_sold(self):
        return self.state == PhotoCardState.SOLD and self.sold_date is not None and self.buyer is not None

    def get_total_price(self):
        return self.price + self.fee

    def set_total_price(self):
        self._total_price = self.get_total_price()
        return self

    def apply_fee_policy(self, fee_policy: FeePolicy):
        self.fee = fee_policy.apply(self.price)
        return self

    def __str__(self):
        return f'Id:{self.id} | 카드: {self.photo_card.name} |가격: {self.price} | 판매자: {self.seller.email} | 구매자: {self.buyer.email}'
