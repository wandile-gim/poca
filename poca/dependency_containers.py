from dependency_injector import containers, providers

from poca.application.adapter.spi.persistence.repository.photo_card_trade_repository import PhotoCardSaleRepository
from poca.application.adapter.spi.persistence.repository.user_repository import UserRepository
from poca.application.service.photo_card_trade_service import PhotoCardTradeService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".application.adapter.api.http", ])

    # repository container
    user_repository = providers.Factory(UserRepository)
    photo_card_sales_repository = providers.Factory(PhotoCardSaleRepository)

    # service container
    photo_card_trade_use_case = providers.Factory(
        PhotoCardTradeService,
        find_user_port=user_repository,
        save_user_port=user_repository,
        find_photo_card_port=photo_card_sales_repository,
        save_photo_card_port=photo_card_sales_repository,
    )
