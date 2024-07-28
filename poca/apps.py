from typing import Dict, Any

from django.apps import AppConfig


class PocaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "poca"

    def ready(self):
        from poca.dependency_containers import Container
        container = Container()
        container.init_resources()
        container.wire(modules=[
            "poca.application.adapter.api.http.photo_card_trade_views",
            "poca.dependency_containers",
        ])
