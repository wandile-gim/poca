from typing import Protocol

from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import OnSaleQueryStrategy
from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand


class PhotoCardTradeUseCase(Protocol):
    def on_sale_photo_card(self, method: OnSaleQueryStrategy):
        """
        조회 정책에 따라 판매중인 포토카드 조회
        :param method: OnSaleQueryStrategy
        """
        raise NotImplementedError()

    def register_photo_card_on_sale(self, command: RegisterPhotoCardOnSaleCommand):
        """
        포토카드 판매 등록
        :param command: RegisterPhotoCardOnSaleCommand
        :param 추가적으로 정책 서비스를 등록가능(수수료)
        """
        raise NotImplementedError()

    def get_recently_sold_photo_card(self, card_id, number_of_cards=5) -> photo_card_trade_result.PhotoCardTradeResult:
        """
        포토카드 정보 및 최근 거래된 지정된 갯수 만큼의 포토카드 거래 내역 조회
        :param card_id: int
        :param number_of_cards: int default: 5
        :return: 조회에 성공했을 경우 PhotoCard 도메인과 PhotoCardSale 도메인 리스트 반환
        """
        raise NotImplementedError()

    def get_min_price_photo_card_on_sale(self, card_id):
        """
        최소 가격의 판매중인 포토카드 조회
        :param card_id: int
        :return: 조회에 성공했을 경우 PhotoCardSale 도메인 반환
        """
        raise NotImplementedError()

    def buy_photo_card_on_record(self, record_id: int,
                                 buyer_id: int) -> photo_card_trade_result.PhotoCardTradeResult:
        """
        판매중인 포토카드를 구매합니다
        :param record_id: int 판매 기록 id
        :param buyer_id: int 구매자 id
        :return: 구매에 성공했을 경우 성공객체 반환, 실패했을 경우 실패객체(NoPhotoCardOnSaleResult, InsufficientBalanceResult, PhotoCardTradeNotProcessedResult) 반환
        """
        raise NotImplementedError()
