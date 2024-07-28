from typing import Protocol, List

from poca.application.domain.model.photo_card import PhotoCard, PhotoCardSale


class FindPhotoCardSalePort(Protocol):
    def find_photo_card_renewal_old(self) -> List[PhotoCardSale]:
        raise NotImplementedError()

    def find_photo_card_by_card_id(self, card_id: int, number_of_cards: int) -> List[PhotoCardSale]:
        raise NotImplementedError()

    def find_sales_record_by_id(self, record_id: int) -> PhotoCardSale:
        raise NotImplementedError()

    def find_min_price_photo_card_on_sale(self, card_id: int) -> PhotoCardSale:
        raise NotImplementedError()
