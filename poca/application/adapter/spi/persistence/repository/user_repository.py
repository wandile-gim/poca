import decimal
import logging

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
            return UserDomain(user.user_email, user.password, user.id, active=user.active)
        except User.DoesNotExist:
            return None

    def get_user_by_user_id(self, user_id: int) -> UserDomain:
        try:
            user = User.objects.get(id=user_id)
            return UserDomain(email=user.user_email, user_id=user.id, active=user.is_active, balance=user.balance)
        except User.DoesNotExist:
            return None

    def save_user_balance(self, user_id: int, balance: decimal.Decimal) -> bool:
        try:
            user = User.objects.get(id=user_id)
            user.balance = balance
            user.save()
        except Exception as e:
            self.logger.error(f"Failed to save user balance: {e}")
            return False

        return True
