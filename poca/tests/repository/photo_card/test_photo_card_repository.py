import datetime
import threading

from django.db import OperationalError, transaction
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import now
from sqlalchemy.dialects.postgresql import psycopg2

from poca.application.adapter.spi.persistence.entity.photo_card import PhotoCardSale, PhotoCard
from poca.application.adapter.spi.persistence.entity.user import User
from poca.application.adapter.spi.persistence.repository.photo_card_trade_repository import PhotoCardSaleRepository
from poca.application.domain.model.photo_card import PhotoCardState
from poca.application.port.api.command.photo_card_trade_command import UpdatePhotoCardCommand
from poca.application.util import transactional
from poca.application.util.transactional import MaxRetriesExceededException


class TestPhotoCardRepository(TestCase):
    repository = None
    card_id: int
    seller: User
    buyer: User

    def setUp(self):
        self.repository = PhotoCardSaleRepository()
        self._init_user()
        self._init_photo_card_sale_datas()

    def _init_user(self):
        self.seller = User.objects.create(
            user_email="seller@test.com", )
        self.buyer = User.objects.create(
            user_email="buyer@test.com", )

    def _init_photo_card_sale_datas(self):
        standard_date = now()

        self.card_id = PhotoCard.objects.create(
            name='테스트',
            description='테스트',
            image_url='https://test.com',
            release_date=standard_date
        ).id

        PhotoCardSale.objects.bulk_create(
            [
                PhotoCardSale(
                    seller=self.seller,
                    buyer=self.buyer,
                    photo_card_id=self.card_id,
                    price=1000,
                    fee=100,
                    renewal_date=standard_date,
                    state=PhotoCardState.ON_SALE.value,
                ),
                PhotoCardSale(
                    seller=self.seller,
                    buyer=self.buyer,
                    photo_card_id=self.card_id,
                    price=100,
                    fee=100,
                    renewal_date=standard_date,
                    state=PhotoCardState.ON_SALE.value,
                ),
                PhotoCardSale(
                    seller=self.seller,
                    buyer=self.buyer,
                    photo_card_id=self.card_id,
                    price=100,
                    fee=100,
                    renewal_date=standard_date,
                    state=PhotoCardState.ON_SALE.value,
                )
            ]
        )

    def test_find_photo_card_renewal_old_최소가격까지_같다면_등록일이_빠른객체_조회한다(self):
        # given
        # 최소가격까지 같은_등록일이_빠른_객체_생성
        PhotoCardSale(
            seller=self.seller,
            buyer=self.buyer,
            photo_card_id=self.card_id,
            price=100,
            fee=100,
            renewal_date=now() - datetime.timedelta(days=1),
            state=PhotoCardState.ON_SALE.value,
        ).save(),

        # when
        # 조회힌다.
        result = self.repository.find_photo_card_renewal_old()

        # then
        # 검증한다.
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 4)

    def test_find_photo_card_renewal_old_포토카드_id가_여러개라면_최소가격_객체만_조회한다(self):
        # given
        PhotoCardSale(
            seller=self.seller,
            buyer=self.buyer,
            photo_card_id=self.card_id,
            price=50,
            fee=100,
            renewal_date=now() - datetime.timedelta(days=1),
            state=PhotoCardState.ON_SALE.value,
        ).save(),

        # when
        result = self.repository.find_photo_card_renewal_old()

        # then
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].price, 50)

    def test_find_photo_card_renewal_old_포토카드_id가_여러개라면_판매중만_조회한다(self):
        # given
        given_id = PhotoCard.objects.create(name='단건').id
        # 새로운 포토카드 객체 생성
        PhotoCardSale(
            seller=self.seller,
            buyer=self.buyer,
            photo_card_id=given_id,
            price=99,
            fee=100,
            renewal_date=now() - datetime.timedelta(days=1),
            state=PhotoCardState.ON_SALE.value,
        ).save(),

        # when
        result = self.repository.find_photo_card_renewal_old()

        # then
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r.state, PhotoCardState.ON_SALE)

    def test_최근거래가_6건_있을_때_디폴트_5건만_조회한다(self):
        # given
        sold_date = now()
        given = [PhotoCardSale(
            seller=self.seller,
            buyer=self.buyer,
            photo_card_id=self.card_id,  # card_id = 1
            price=1000,
            fee=100,
            renewal_date=now(),
            state=PhotoCardState.ON_SALE.value,
            sold_date=sold_date
        ) for _ in range(6)]

        # 최근 거래인지 확인하기 위해 1건 더 생성
        PhotoCardSale(
            seller=self.seller,
            buyer=self.buyer,
            photo_card_id=self.card_id,
            price=10000,
            fee=100,
            renewal_date=now(),
            state=PhotoCardState.ON_SALE.value,
            sold_date=sold_date + datetime.timedelta(days=1)
        ).save()

        def bulk():
            PhotoCardSale.objects.bulk_create(given)

        bulk()

        # when
        result = self.repository.find_photo_card_by_card_id(1, 5)

        # then
        # 5건이 조회되는지 검증
        self.assertEqual(len(result), 5)
        # 5건 중 가장 최근에 팔린 가격이 10000인지 검증
        self.assertEqual(result[0].price, 10000)
        # 5건 중 가장 오래된 가격이 1000인지 검증
        self.assertEqual(result[len(result) - 1].price, 1000)


class TestPhotoCardRepositorySavePort(TransactionTestCase):
    repository = None
    card_id: int
    seller: User
    buyer1: User
    buyer2: User

    def setUp(self):
        self.repository = PhotoCardSaleRepository()
        self._init_user()
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED;')

    def _init_user(self):
        self.seller = User.objects.create(
            user_email="seller@test.com")
        self.buyer1 = User.objects.create(
            user_email="buyer1@test.com")
        self.buyer2 = User.objects.create(
            user_email="buyer2@test.com")

    def test_update시에_충돌을_감지하는지_확인(self):
        # given
        # 포토카드 객체 생성
        photo_card = PhotoCard.objects.create(
            name='테스트',
        )
        # 포토카드 판매 객체 생성
        photo_card_sale = PhotoCardSale.objects.create(
            seller_id=self.seller.id,
            photo_card_id=photo_card.id,
            price=1000,
            fee=100,
            renewal_date=now(),
            state=PhotoCardState.ON_SALE.value,
        )

        n = now()
        photo_card_sale.sold_date = n

        # when
        thread1 = threading.Thread(target=self.repository.update_photo_card_sale,
                                   args=(UpdatePhotoCardCommand(photo_card_sale.id, self.buyer1.id,
                                                                version=photo_card_sale.version),))
        thread2 = threading.Thread(target=self.repository.update_photo_card_sale,
                                   args=(UpdatePhotoCardCommand(photo_card_sale.id, self.buyer2.id,
                                                                version=photo_card_sale.version),))
        print(PhotoCardSale.objects.get(id=photo_card_sale.id).version)
        try:
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
        except MaxRetriesExceededException as e:
            print(e)


        # then
        updated_photo_card_sale = PhotoCardSale.objects.get(id=photo_card_sale.id)
        print(updated_photo_card_sale.version)
        self.assertIn(updated_photo_card_sale.buyer_id, [self.buyer1.id, self.buyer2.id])

