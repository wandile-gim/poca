import dataclasses
import decimal
import enum

from poca.application.domain.model.user import UserDomain


class PhotoCardState(enum.Enum):
    ON_SALE = "판매중"
    SOLD = "판매완료"


@dataclasses.dataclass
class PhotoCard:
    id: int
    name: str
    description: str
    image_url: str
    release_date: str

    def __str__(self):
        return f'Id:{self.id} | 카드 이름: {self.name}'


@dataclasses.dataclass
class PhotoCardSale:
    id: int
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

    def is_sold(self):
        return self.state == PhotoCardState.SOLD and self.sold_date is not None and self.buyer is not None

    def get_total_price(self):
        return self.price + self.fee

    def __str__(self):
        return f'Id:{self.id} | 카드: {self.photo_card.name} |가격: {self.price} | 판매자: {self.seller.email} | 구매자: {self.buyer.email}'
