from typing import Protocol, List

from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import PhotoCardSale
from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand


class PhotoCardTradeUseCase(Protocol):
    def on_sale_photo_card(self, method: str):
        raise NotImplementedError()

    def register_photo_card_on_sale(self, command: RegisterPhotoCardOnSaleCommand):
        """
        포토카드 판매 등록
        :param command: RegisterPhotoCardOnSaleCommand
        :param 추가적으로 정책 서비스를 등록가능(수수료)
        """
        raise NotImplementedError()

    def get_recently_sold_photo_card(self, card_id, number_of_cards) -> List[PhotoCardSale]:
        raise NotImplementedError()

    def get_min_price_photo_card_on_sale(self, card_id):
        raise NotImplementedError()

    def buy_photo_card_on_record(self, record_id: int,
                                 buyer_id: int) -> photo_card_trade_result.PhotoCardTradeResult:
        raise NotImplementedError()
