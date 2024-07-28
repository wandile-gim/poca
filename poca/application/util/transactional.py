import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from django.db import transaction

T = TypeVar('T')
P = ParamSpec('P')


def transactional(f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        with transaction.atomic():
            return f(*args, **kwargs)

    return inner


class OptimisticLockException(Exception):
    pass


class MaxRetriesExceededException(Exception):
    pass


def retry_optimistic_locking(retries=3) -> Callable[P, T]:
    """
    낙관적 락 충돌이 발생할 경우 재시도하는 데코레이터
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except OptimisticLockException as e:
                    print(f"OptimisticLockException occurred. Retrying... (attempt {attempts + 1}/{retries})")
                    if attempts < retries - 1:
                        time.sleep(1)  # 재시도 간 대기 시간 조절
                        attempts += 1
                        continue
                    else:
                        raise MaxRetriesExceededException("Max retries exceeded due to version conflict.") from e
        return wrapper
    return decorator
