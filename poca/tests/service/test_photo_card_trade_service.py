import decimal

from django.test import TestCase

from poca.application.adapter.spi.persistence.entity.user import User
from poca.application.adapter.spi.persistence.repository.photo_card_repository import PhotoCardRepository
from poca.application.adapter.spi.persistence.repository.photo_card_trade_repository import PhotoCardSaleRepository
from poca.application.adapter.spi.persistence.repository.user_repository import UserRepository
from poca.application.domain.model.photo_card import OnSaleQueryStrategy, PhotoCardSale, PhotoCardState
from poca.application.domain.model.photo_card_trade_result import PhotoCardSaleRegisteredResult, NoPhotoCardOnSaleResult
from poca.application.port.api.command.photo_card_command import CreatePhotoCardCommand
from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand
from poca.application.service.photo_card_trade_service import PhotoCardTradeService


class TestPhotoCardTradeService(TestCase):
    photo_repository: PhotoCardRepository
    photo_trade_repository: PhotoCardSaleRepository
    user_repository: UserRepository
    service: PhotoCardTradeService

    def setUp(self):
        self.user_repository = UserRepository()
        self.photo_repository = PhotoCardRepository()
        self.photo_trade_repository = PhotoCardSaleRepository()
        self.service = PhotoCardTradeService(
            self.user_repository,
            self.user_repository,
            self.photo_trade_repository,
            self.photo_trade_repository
        )

        self.buyer_1 = User.objects.create(
            user_email="buyer1@poca.com")
        self.buyer_2 = User.objects.create(
            user_email="buyer2@poca.com")

    def test_register_photo_card_on_sale(self):
        # given
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        result = self.service.register_photo_card_on_sale(RegisterPhotoCardOnSaleCommand(
            card_id=card_id,
            price=1000,
            seller_id=self.buyer_1.id,
            fee=100))

        # then
        print(result.to_message())
        self.assertIsInstance(result, PhotoCardSaleRegisteredResult)

    def test_on_sale_photo_card_동일한_판매가_여러건이라면_최소가격만_조회(self):
        # given
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        result = self.service.on_sale_photo_card(OnSaleQueryStrategy.MIN_PRICE_RENEWAL_LATE_FIRST)
        self.assertEqual(result[0].get_total_price(), decimal.Decimal(1100))

    def test_on_sale_photo_card_동일한_판매가_여러건이고_최소금액도_같다면_수정이_먼저된것만_조회(self):
        # given
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2020-01-01"
        ))
        result = self.service.on_sale_photo_card(OnSaleQueryStrategy.MIN_PRICE_RENEWAL_LATE_FIRST)

        self.assertEqual(result[0].get_total_price(), decimal.Decimal(1100))
        self.assertEqual(len(result), 1)

    def test_get_recently_sold_photo_card(self):
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        record_id = self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        # when
        # 포토카드를 구매 했을 때 구매 조회
        self.service.buy_photo_card_on_record(record_id.id, self.buyer_2.id)
        result = self.service.get_recently_sold_photo_card(card_id, 2)

        # then
        self.assertEqual(result.photo_card_sales[0].get_total_price(), decimal.Decimal(1100))

    def test_get_min_price_photo_card_on_sale(self):
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))

        result = self.service.get_min_price_photo_card_on_sale(card_id)
        self.assertEqual(result.record.get_total_price(), decimal.Decimal(1100))

    def test_buy_photo_card_on_record(self):
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        record_id = self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))

        # when
        # 포토카드를 구매 했을 때 구매 조회
        self.service.buy_photo_card_on_record(record_id.id, self.buyer_2.id)

        # then
        # 구매한 포토카드의 상태가 판매완료로 변경되었는지 확인
        result = self.photo_trade_repository.find_sales_record_by_id(record_id.id)
        self.assertEqual(result.state.value, PhotoCardState.SOLD.value)

    def test_get_min_price_photo_card_on_sale(self):
        card_id = self.photo_repository.register_new_photo_card(CreatePhotoCardCommand(
            name="test",
            description="test",
            image_data=b"test"
        ))

        # when
        self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(10001),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))
        record_id = self.photo_trade_repository.save_photo_card_sale(PhotoCardSale(
            state=PhotoCardState.ON_SALE.value,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            seller_id=self.buyer_1.id,
            photo_card_id=card_id,
            renewal_date="2021-01-01"
        ))

        # when
        result = self.service.get_min_price_photo_card_on_sale(card_id)

        # 찾으려는 포토카드가 없을 경우
        no_card_id = -1
        result2 = self.service.get_min_price_photo_card_on_sale(no_card_id)

        self.assertEqual(result.record.get_total_price(), decimal.Decimal(1100))
        self.assertIsInstance(result2, NoPhotoCardOnSaleResult)
