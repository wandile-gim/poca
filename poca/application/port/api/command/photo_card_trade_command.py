import uuid
from dataclasses import dataclass


@dataclass
class UpdatePhotoCardCommand:
    record_id: int
    buyer_id: int
    version: int


@dataclass
class RegisterPhotoCardOnSaleCommand:
    card_id: int
    seller_id: int
    price: int
    fee: int = 0
