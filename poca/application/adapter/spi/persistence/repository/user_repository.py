import decimal
import logging
import uuid

from poca.application.adapter.spi.persistence.entity.user import User
from poca.application.domain.model.user import UserDomain
from poca.application.port.spi.repository.user.find_user_port import FindUserPort
from poca.application.port.spi.repository.user.save_user_port import SaveUserPort


class UserRepository(
    FindUserPort,
    SaveUserPort
):
    logger = logging.getLogger(__name__)

    def get_user_by_user_email(self, email: str) -> UserDomain:
        try:
            user = User.objects.get(email=email)
            return UserDomain(user.email, user.password, user.user_id, active=user.active)
        except User.DoesNotExist:
            return None

    def get_user_by_user_id(self, user_id: int) -> UserDomain:
        try:
            user = User.objects.get(user_id=user_id)
            return UserDomain(user.email, user.password, user.user_id, active=user.active)
        except User.DoesNotExist:
            return None

    def save_user_balance(self, user_id: int, balance: decimal.Decimal) -> bool:
        try:
            user = User.objects.get(user_id=user_id)
            user.balance = balance
            user.save()
        except Exception as e:
            self.logger.error(f"Failed to save user balance: {e}")
            return False

        return True
