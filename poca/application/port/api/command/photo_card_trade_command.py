from dataclasses import dataclass


@dataclass
class UpdatePhotoCardCommand:
    """
    포토 카드 구매 정보 업데이트를 위한 시그니처 클래스
    """
    record_id: int
    buyer_id: int
    version: int


@dataclass
class RegisterPhotoCardOnSaleCommand:
    """
    판매중인 포토카드 등록을 위한 시그니처 클래스
    """
    card_id: int
    seller_id: int
    price: int
    fee: int = 0
