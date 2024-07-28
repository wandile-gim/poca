from dataclasses import dataclass

from poca.application.domain.model.photo_card import PhotoCardSale


class PhotoCardTradeResult:
    """
    Service Layer에서 처리된 결과를 반환하기 위한 상위 클래스
    """

    def to_message(self) -> str:
        raise NotImplementedError()


@dataclass
class PhotoCardTradeResultObject(PhotoCardTradeResult):
    record: PhotoCardSale


@dataclass
class InsufficientBalanceResult(PhotoCardTradeResult):
    user_id: int

    def to_message(self) -> str:
        return f"user_id:{self.user_id} 구매에 충분한 잔액을 가지고 있지 않습니다."


@dataclass
class PhotoCardSaleRegisterFailResult(PhotoCardTradeResult):
    """
    판매 등록 실패
    """
    photo_card_id: int

    def to_message(self) -> str:
        return f"photo_card_id:{self.photo_card_id} 판매 등록에 실패하였습니다."


@dataclass
class PhotoCardSaleRegisteredResult(PhotoCardTradeResult):
    """
    판매 등록 성공
    """
    photo_card_id: int

    def to_message(self) -> str:
        return f"photo_card_id:{self.photo_card_id} 판매 등록이 완료되었습니다."


@dataclass
class NoPhotoCardOnSaleResult(PhotoCardTradeResult):
    photo_card_id: int

    def to_message(self) -> str:
        return f"photo_card_id:{self.photo_card_id} 판매 중인 포토카드가 없습니다."


@dataclass
class PhotoCardTradeProcessedResult(PhotoCardTradeResult):
    record_id: int

    def to_message(self) -> str:
        return f"record_id:{self.record_id} 거래가 성공적으로 처리되었습니다."


@dataclass
class PhotoCardTradeNotProcessedResult(PhotoCardTradeResult):
    record_id: int

    def to_message(self) -> str:
        return f"record_id:{self.record_id} 거래가 처리되지 않았습니다. 재시도 해주세요."

