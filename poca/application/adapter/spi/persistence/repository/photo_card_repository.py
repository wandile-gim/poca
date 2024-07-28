import logging
from typing import List, Optional

from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Subquery
from django.utils.timezone import now

from poca.application.adapter.spi.persistence.entity.photo_card import PhotoCardSale
from poca.application.domain.model.photo_card import PhotoCardSale as PhotoCardSaleDomain
from poca.application.domain.model.photo_card import PhotoCardState
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand
from poca.application.port.spi.repository.product.find_photo_card_port import FindPhotoCardSalePort
from poca.application.port.spi.repository.product.save_photo_card_port import SavePhotoCardPort
from poca.application.util.transactional import retry_optimistic_locking, OptimisticLockException


class PhotoCardRepository(
    FindPhotoCardSalePort,
    SavePhotoCardPort
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

        return [photo_card.to_domain()
                for photo_card in result]

    def find_photo_card_by_card_id(self, card_id: int, number_of_cards: int = 5) -> List[PhotoCardSaleDomain]:
        return [
            record.to_domain() for record in PhotoCardSale.objects.filter(
                photo_card_id=card_id,
                sold_date__isnull=False).order_by('-sold_date')[:number_of_cards]
        ]

    def find_sales_record_by_id(self, record_id: int) -> PhotoCardSale:
        return PhotoCardSale.objects.get(id=record_id)

    def find_min_price_photo_card_on_sale(self, card_id: int) -> Optional[PhotoCardSale]:
        try:
            return PhotoCardSale.objects.filter(
                photo_card_id=card_id,
                state=PhotoCardState.ON_SALE.value
            ).order_by('price').first()
        except PhotoCardSale.DoesNotExist:
            return

    def save_photo_card(self, photo_card: PhotoCardSaleDomain) -> bool:
        try:
            PhotoCardSale(
                photo_card_id=photo_card.photo_card.id,
                state=photo_card.state.value,
                price=photo_card.price,
                fee=photo_card.fee,
                seller_id=photo_card.seller.user_id,
                create_date=photo_card.create_date,
                renewal_date=photo_card.renewal_date,
            ).save()
        except IntegrityError:
            self.logger.error(f'PhotoCardSale save error {photo_card}')
            return False
        return True

    @retry_optimistic_locking(retries=2)
    @transaction.atomic
    def update_photo_card(self, command: UpdatePhotoCardCommand):
        sold_date = now()
        try:
            # 대상 레코드 조회

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
