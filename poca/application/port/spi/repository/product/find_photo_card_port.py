from typing import Protocol, List, Optional

from poca.application.domain.model.photo_card import PhotoCard, PhotoCardSale


class FindPhotoCardSalePort(Protocol):
    def find_photo_card_renewal_old(self) -> List[PhotoCardSale]:
        """
        리뉴얼이 오래된 포토카드 조회, 포토 카드 당 판매중이면서 최소 가격인 포토카드 조회 최소가격이 같을 경우 리뉴얼이 오래된 순으로 반환
        :return: [domain] List:PhotoCardSale
        """
        raise NotImplementedError()

    def find_photo_card_by_card_id(self, card_id: int) -> Optional[PhotoCard]:
        """
        포토카드 id를 가진 포토카드 조회
        :param card_id: int
        :return: Optional[PhotoCardDomain]
        """
        raise NotImplementedError()

    def find_recently_sold_photo_card(self, card_id: int, number_of_cards: int) -> List[PhotoCardSale]:
        """
        최근 판매된 포토카드 조회
        :param card_id: int
        :param number_of_cards: int default: 5
        :return: [domain] List:PhotoCardSale
        """
        raise NotImplementedError()

    def find_sales_record_by_id(self, record_id: int) -> PhotoCardSale:
        """
        판매 기록 id를 가진 판매 기록 조회
        :param record_id: int
        :return: [domain] PhotoCardSale
        """
        raise NotImplementedError()

    def find_min_price_photo_card_on_sale(self, card_id: int) -> PhotoCardSale:
        """
        최소 가격의 판매중인 포토카드 조회
        :param card_id: int
        :return: [domain] PhotoCardSale
        """
        raise NotImplementedError()
