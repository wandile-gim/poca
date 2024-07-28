from typing import Protocol

from poca.application.domain.model.photo_card import PhotoCardSale
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand, \
    RegisterPhotoCardOnSaleCommand


class SavePhotoCardSalePort(Protocol):
    def save_photo_card_sale(self, photo_card: PhotoCardSale) -> PhotoCardSale:
        """
        신규 포토카드 판매 정보 저장
        :param photo_card: RegisterPhotoCardOnSaleCommand
        """
        raise NotImplementedError()

    def update_photo_card_sale(self, command: UpdatePhotoCardCommand):
        """
        포토 카드 구매 정보 업데이트 version을 이용한 동시성 제어
        :param command: UpdatePhotoCardCommand
        """
        raise NotImplementedError()
