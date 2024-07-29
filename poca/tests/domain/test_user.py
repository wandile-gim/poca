import decimal
from unittest import TestCase

from poca.application.domain.model.user import UserDomain


class TestUserDomain(TestCase):
    def test_is_user_can_purchase(self):
        # given
        card_price = decimal.Decimal(1000)
        user = UserDomain(1, decimal.Decimal(10000), "", True)

        # then
        self.assertTrue(user.is_user_can_purchase(card_price))

    def test_buy_photo_card(self):
        # given
        card_price = decimal.Decimal(1000)
        user = UserDomain(1, decimal.Decimal(10000), "", True)

        # when
        user.buy_photo_card(card_price)

        # then
        self.assertEqual(user.balance, decimal.Decimal(9000))
