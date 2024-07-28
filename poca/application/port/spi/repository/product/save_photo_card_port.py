from typing import Protocol

from poca.application.domain.model.photo_card import PhotoCardSale
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand


class SavePhotoCardPort(Protocol):
    def save_photo_card(self, photo_card: PhotoCardSale) -> bool:
        raise NotImplementedError()

    def update_photo_card(self, command: UpdatePhotoCardCommand):
        raise NotImplementedError()
