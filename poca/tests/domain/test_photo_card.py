import decimal
from unittest import TestCase

from poca.application.domain.model.photo_card import PhotoCardSale, PhotoCardState, PhotoCard, FeePolicy


class TestPhotoCardSale(TestCase):
    def setUp(self):
        photo_card = PhotoCard(
            id=1,
            name="test",
            description="test",
            release_date="2021-01-01",
            image_url="https://test.com"
        )
        self.photo_card_sale = PhotoCardSale(
            photo_card=photo_card,
            state=PhotoCardState.ON_SALE,
            price=decimal.Decimal(1000),
            fee=decimal.Decimal(100),
            sold_date=""
        )

    def test_is_sold(self):
        self.assertFalse(self.photo_card_sale.is_sold())

    def test_get_total_price(self):
        self.assertEqual(self.photo_card_sale.get_total_price(), decimal.Decimal(1100))

    def test_set_total_price(self):
        self.assertIsInstance(self.photo_card_sale.set_total_price(), PhotoCardSale)
        self.assertEqual(self.photo_card_sale.get_total_price(), decimal.Decimal(1100))

    def test_apply_fee_policy(self):
        promotion = FeePolicy(discount_percentage=decimal.Decimal(5))
        self.photo_card_sale.apply_fee_policy(promotion)
        self.assertEqual(self.photo_card_sale.get_total_price(), decimal.Decimal(1050))
