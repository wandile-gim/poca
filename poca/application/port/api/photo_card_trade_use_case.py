import uuid
from typing import Protocol, List

from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import PhotoCardSale


class PhotoCardTradeUseCase(Protocol):
    def on_sale_photo_card(self, method: str):
        raise NotImplementedError()

    def get_recently_sold_photo_card(self, card_id, number_of_cards) -> List[PhotoCardSale]:
        raise NotImplementedError()

    def get_min_price_photo_card_on_sale(self, card_id):
        raise NotImplementedError()

    def buy_photo_card_on_record(self, record_id: int,
                                 buyer_id: int) -> photo_card_trade_result.PhotoCardTradeResult:
        raise NotImplementedError()
