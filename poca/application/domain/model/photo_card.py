import dataclasses
import decimal
import enum

from poca.application.domain.model.user import UserDomain


class OnSaleQueryStrategy(enum.Enum):
    MIN_PRICE_RENEWAL_LATE_FIRST = "MIN_PRICE_RENEWAL_LATE_FIRST"


class PhotoCardState(enum.Enum):
    ON_SALE = "판매중"
    SOLD = "판매완료"


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
    photo_card: PhotoCard
    state: PhotoCardState
    price: decimal.Decimal
    fee: decimal.Decimal
    seller: UserDomain
    buyer: UserDomain
    create_date: str
    renewal_date: str
    sold_date: str
    version: int = 0
    id: int = None
    total_price: decimal.Decimal = None
    photo_card_id: int = None
    buyer_id: int = None
    seller_id: int = None

    def is_sold(self):
        return self.state == PhotoCardState.SOLD and self.sold_date is not None and self.buyer is not None

    def get_total_price(self):
        return self.price + self.fee

    def set_total_price(self):
        self.total_price = self.get_total_price()
        return self

    @staticmethod
    def get_fee(self):
        """
        수수료 계산 정책에 따라 수수료를 계산
        """

        # 수수료 계산 정책
        # 10% 수수료
        self.fee = self.price * 0.1
        return self.fee



    def __str__(self):
        return f'Id:{self.id} | 카드: {self.photo_card.name} |가격: {self.price} | 판매자: {self.seller.email} | 구매자: {self.buyer.email}'
