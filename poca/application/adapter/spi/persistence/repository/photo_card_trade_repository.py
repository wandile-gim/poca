import logging
from typing import List, Optional

from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Subquery
from django.utils.timezone import now

from poca.application.adapter.spi.persistence.entity.photo_card import PhotoCardSale, PhotoCard
from poca.application.domain.model.photo_card import PhotoCard as PhotoCardDomain
from poca.application.domain.model.photo_card import PhotoCardSale as PhotoCardSaleDomain
from poca.application.domain.model.photo_card import PhotoCardState
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand
from poca.application.port.spi.repository.product.find_photo_card_port import FindPhotoCardSalePort
from poca.application.port.spi.repository.product.save_photo_card_port import SavePhotoCardSalePort
from poca.application.util.transactional import retry_optimistic_locking, OptimisticLockException


class PhotoCardSaleRepository(
    FindPhotoCardSalePort,
    SavePhotoCardSalePort
):
    logger = logging.getLogger(__name__)

    def find_photo_card_renewal_old(self) -> List[PhotoCardSaleDomain]:
        # 최소 가격, 리뉴얼을 만족하는 쿼리를 찾는 서브 쿼리
        subquery = PhotoCardSale.objects.filter(
            state=PhotoCardState.ON_SALE.value,
            photo_card_id=OuterRef('photo_card_id')
        ).order_by('price', 'renewal_date').values('id')[:1]

        # 각 photo_card_id별로 조건을 만족하는 객체를 찾는 쿼리
        result = PhotoCardSale.objects.filter(id__in=Subquery(subquery))

        return [photo_card.to_domain().set_total_price()
                for photo_card in result]

    def find_recently_sold_photo_card(self, card_id: int, number_of_cards: int = 5) -> List[PhotoCardSaleDomain]:
        return [
            record.to_domain().set_total_price() for record in PhotoCardSale.objects.filter(
                photo_card_id=card_id,
                sold_date__isnull=False).order_by('-sold_date')[:number_of_cards]
        ]

    def find_sales_record_by_id(self, record_id: int) -> PhotoCardSaleDomain:
        """
        판매 기록 id를 가진 판매 기록 조회
        :param record_id: int
        """
        return PhotoCardSale.objects.get(id=record_id).to_domain()

    def find_min_price_photo_card_on_sale(self, card_id: int) -> Optional[PhotoCardSale]:
        """
        최소 가격의 판매중인 포토카드 조회
        :param card_id: int
        """
        query = PhotoCardSale.objects.filter(
            photo_card_id=card_id,
            state=PhotoCardState.ON_SALE.value
        ).order_by('price')
        if query.exists():
            return query.first().to_domain()
        return None

    def save_photo_card_sale(self, photo_card: PhotoCardSaleDomain) -> PhotoCardSaleDomain:
        """
        신규 포토카드 판매 정보 저장
        :param photo_card: RegisterPhotoCardOnSaleCommand
        """
        try:
            sale = PhotoCardSale(
                state=PhotoCardState.ON_SALE.value,
                price=photo_card.price,
                fee=photo_card.fee,
                seller_id=photo_card.seller_id,
                photo_card_id=photo_card.photo_card_id,
                renewal_date=photo_card.renewal_date
            )
            sale.save()
            return sale.to_domain()

        except IntegrityError:
            self.logger.error(f'PhotoCardSale save error {photo_card}')
            return None

    @retry_optimistic_locking(retries=2)
    @transaction.atomic
    def update_photo_card_sale(self, command: UpdatePhotoCardCommand):
        """
        포토 카드 구매 정보 업데이트 version을 이용한 동시성 제어
        :param command: UpdatePhotoCardCommand
        """
        sold_date = now()
        try:
            # 대상 레코드 조회 및 업데이트
            # 일치하는 버전이
            updated_count = PhotoCardSale.objects.filter(
                id=command.record_id,
                version=command.version
            ).update(
                buyer_id=command.buyer_id,
                sold_date=sold_date,
                state=PhotoCardState.SOLD.value,
                version=command.version + 1
            )
            # 업데이트된 값이 0이면 낙관적 락 충돌이 발생
            if updated_count == 0:
                raise OptimisticLockException('PhotoCardSale version mismatch')

        except PhotoCardSale.DoesNotExist:
            self.logger.error(f'PhotoCardSale not found {command.record_id}')
            # return False
        except Exception as e:
            raise e

    def find_photo_card_by_card_id(self, card_id: int) -> Optional[PhotoCardDomain]:
        """
         포토카드 id를 가진 포토카드 조회
         :param card_id: int
         :return: Optional[PhotoCardDomain]
         """
        try:
            return PhotoCard.objects.get(id=card_id).to_domain()
        except PhotoCard.DoesNotExist:
            return None
