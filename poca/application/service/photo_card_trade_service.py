import decimal
import logging
from typing import List

from django.db import transaction
from django.utils.timezone import now

from poca.application.adapter.spi.persistence.repository.user_repository import FindUserPort
from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import PhotoCardSale, PhotoCardState, FeePolicy, OnSaleQueryStrategy
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand, \
    RegisterPhotoCardOnSaleCommand
from poca.application.port.api.photo_card_trade_use_case import PhotoCardTradeUseCase
from poca.application.port.spi.repository.product.find_photo_card_port import FindPhotoCardSalePort
from poca.application.port.spi.repository.product.save_photo_card_port import SavePhotoCardSalePort
from poca.application.port.spi.repository.user.save_user_port import SaveUserPort
from poca.application.util.transactional import MaxRetriesExceededException


class PhotoCardTradeService(
    PhotoCardTradeUseCase
):
    _find_user_port: FindUserPort
    _save_user_port: SaveUserPort
    _find_photo_card_port: FindPhotoCardSalePort
    _save_photo_card_port: SavePhotoCardSalePort

    logger = logging.getLogger(__name__)

    def __init__(self, find_user_port: FindUserPort, save_user_port: SaveUserPort,
                 find_photo_card_port: FindPhotoCardSalePort, save_photo_card_port: SavePhotoCardSalePort):
        self._find_user_port = find_user_port
        self._save_user_port = save_user_port
        self._find_photo_card_port = find_photo_card_port
        self._save_photo_card_port = save_photo_card_port

    def register_photo_card_on_sale(self, command: RegisterPhotoCardOnSaleCommand):

        # 판매 등록 성공시 도메인 반환, 실패시 None
        fee = command.fee if command.fee > 0 else FeePolicy(decimal.Decimal(5))
        trade_record = PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(command.price),
            fee=decimal.Decimal(fee),
            seller_id=command.seller_id,
            photo_card_id=command.card_id,
            renewal_date=now()
        )

        if self._save_photo_card_port.save_photo_card_sale(trade_record):
            return photo_card_trade_result.PhotoCardSaleRegisteredResult(command.card_id)
        else:
            return photo_card_trade_result.PhotoCardSaleRegisterFailResult(command.card_id)

    def on_sale_photo_card(self, method: OnSaleQueryStrategy):
        match method:
            case OnSaleQueryStrategy.MIN_PRICE_RENEWAL_LATE_FIRST:
                return self._on_sale_photo_card_by_min_price_renewal_rate_first()

    def _on_sale_photo_card_by_min_price_renewal_rate_first(self) -> List[PhotoCardSale]:
        # 판매중인 포토카드를 조회 저렴한 가격순으로 정렬
        cards = self._find_photo_card_port.find_photo_card_renewal_old()

        return cards

    def get_recently_sold_photo_card(self, card_id, number_of_cards=5) -> photo_card_trade_result.PhotoCardTradeResult:
        if photo_card := self._find_photo_card_port.find_photo_card_by_card_id(card_id):
            trade_list = self._find_photo_card_port.find_recently_sold_photo_card(card_id, number_of_cards)
            return photo_card_trade_result.PhotoCardTradeRecentlySoldResult(trade_list, photo_card)
        else:
            return photo_card_trade_result.NoPhotoCardOnSaleResult(card_id)

    def get_min_price_photo_card_on_sale(self, card_id) -> photo_card_trade_result.PhotoCardTradeResult:
        if result := self._find_photo_card_port.find_min_price_photo_card_on_sale(card_id):
            return photo_card_trade_result.PhotoCardTradeResultObject(result.set_total_price())
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
                self._save_photo_card_port.update_photo_card_sale(UpdatePhotoCardCommand(
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
