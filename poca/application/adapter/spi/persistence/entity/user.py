from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from poca.application.domain.model.user import UserDomain


class UserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        if not user_email:
            raise ValueError('유저 이메일 주소가 필요합니다.')
        user = self.model(user_email=user_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password, **extra_fields):
        user = self.create_user(user_email, password)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user.is_admin = True
        user.is_staff = True
        self.create_user(user_email, password, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    # 유저 생성시 기본 지급 10000원, 0원 밑으로는 설정 불가
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=10000)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'

    def __str__(self):
        return self.user_email

    def to_domain(self):
        return UserDomain(
            user_id=self.id,
            email=self.user_email,
            balance=self.balance,
            active=self.is_active
        )
