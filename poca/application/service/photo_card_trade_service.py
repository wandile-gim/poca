import logging
import uuid
from typing import List

from django.db import transaction

from poca.application.adapter.spi.persistence.repository.user_repository import FindUserPort
from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import PhotoCardSale, PhotoCardState
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand
from poca.application.port.api.photo_card_trade_use_case import PhotoCardTradeUseCase
from poca.application.port.spi.repository.product.find_photo_card_port import FindPhotoCardSalePort
from poca.application.port.spi.repository.product.save_photo_card_port import SavePhotoCardPort
from poca.application.port.spi.repository.user.save_user_port import SaveUserPort
from poca.application.util.transactional import MaxRetriesExceededException

DEFAULT_QUERY_METHOD = 'MIN_PRICE_RENEWAL_LATE_FIRST'


class PhotoCardTradeService(
    PhotoCardTradeUseCase
):
    _find_user_port: FindUserPort
    _save_user_port: SaveUserPort
    _find_photo_card_port: FindPhotoCardSalePort
    _save_photo_card_port: SavePhotoCardPort

    logger = logging.getLogger(__name__)

    def __init__(self, find_user_port: FindUserPort, save_user_port: SaveUserPort,
                 find_photo_card_port: FindPhotoCardSalePort, save_photo_card_port: SavePhotoCardPort):
        self._find_user_port = find_user_port
        self._save_user_port = save_user_port
        self._find_photo_card_port = find_photo_card_port
        self._save_photo_card_port = save_photo_card_port

    def on_sale_photo_card(self, method: str):
        match method:
            case 'MIN_PRICE_RENEWAL_LATE_FIRST':
                self._on_sale_photo_card_by_min_price_renewal_rate_first()

    def _on_sale_photo_card_by_min_price_renewal_rate_first(self) -> List[PhotoCardSale]:
        # 판매중인 포토카드를 조회 저렴한 가격순으로 정렬
        cards = self._find_photo_card_port.find_photo_card_renewal_old()

        return cards

    def get_recently_sold_photo_card(self, card_id, number_of_cards) -> List[PhotoCardSale]:
        result = self._find_photo_card_port.find_photo_card_by_card_id(card_id, number_of_cards)
        return result

    def get_min_price_photo_card_on_sale(self, card_id) -> photo_card_trade_result.PhotoCardTradeResult:
        if result := self._find_photo_card_port.find_min_price_photo_card_on_sale(card_id):
            return photo_card_trade_result.PhotoCardTradeResultObject(result)
        else:
            return photo_card_trade_result.NoPhotoCardOnSaleResult(card_id)

    def buy_photo_card_on_record(self, record_id: int,
                                 buyer_id: int) -> photo_card_trade_result.PhotoCardTradeResult:

        user = self._find_user_port.get_user_by_user_id(buyer_id)
        record = self._find_photo_card_port.find_sales_record_by_id(record_id)

        # 유저가 가진 돈이 충분하지 않을 경우 결과 리턴
        if not user.is_user_can_purchase(record.get_total_price()):
            return photo_card_trade_result.InsufficientBalanceResult(buyer_id)

        # 포토카드가 판매 중이 아닐 경우 결과 리턴
        if record.is_sold():
            return photo_card_trade_result.NoPhotoCardOnSaleResult(record_id)

        try:
            with transaction.atomic():
                self._save_photo_card_port.update_photo_card(UpdatePhotoCardCommand(
                    record_id=record_id,
                    buyer_id=buyer_id,
                    version=record.version
                ))
                user.buy_photo_card(record.get_total_price())
                self._save_user_port.save_user_balance(buyer_id, user.balance)
            return photo_card_trade_result.PhotoCardTradeProcessedResult(record_id)

        except MaxRetriesExceededException:
            return photo_card_trade_result.PhotoCardTradeNotProcessedResult(record_id)
        except Exception as e:
            self.logger.error(f"Failed to buy photo card: {e}")
            return photo_card_trade_result.PhotoCardTradeNotProcessedResult(record_id)
