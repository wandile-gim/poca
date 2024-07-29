from django.apps import AppConfig


class PocaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "poca"

    def ready(self):
        from poca.dependency_containers import Container
        # 의존성 컨테이너 객체 생성
        container = Container()
        container.init_resources()

        # view에서 사용할 서비스를 정의한 컨테이너를 연결
        container.wire(modules=[
            "poca.application.adapter.api.http.photo_card_trade_views",
            "poca.dependency_containers",
        ])
