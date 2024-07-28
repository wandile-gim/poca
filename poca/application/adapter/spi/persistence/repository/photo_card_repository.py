from poca.application.adapter.spi.persistence.entity.photo_card import PhotoCard
from poca.application.port.api.command.photo_card_command import CreatePhotoCardCommand


class PhotoCardRepository:
    """
    포토카드 관련 데이터베이스 처리를 위한 Repository
    """

    def register_new_photo_card(self, photo_card: CreatePhotoCardCommand) -> None:
        """
        새로운 포토카드를 등록한다.
        :param photo_card: PhotoCardDomain 포토카드 도메인객체
        :info: 이미지 url은 async로 처리, 이미지 url은 빈값으로 처리한다.

        """
        photo_card_id = PhotoCard.objects.create(
            name=photo_card.name,
            description=photo_card.description,
        )
        # async로 이미지 url 처리
        self.upload_image_to_s3(photo_card_id.id, photo_card.image_data)

    def upload_image_to_s3(self, photo_card_id: int, image_data: bytes) -> str:
        """
        비동기로 이미지를 S3에 업로드한다.
        :param photo_card_id: int 포토카드 id
        :param image_data: bytes 이미지 데이터
        :return: str 이미지 url
        """
        # S3에 이미지 업로드
        # celery를 사용하여 비동기로 처리 가능
        # 우선은 임시로 temp를 반환하도록 처리
        temp_url = f"https://s3.ap-northeast-2.amazonaws.com/photo-cards/{photo_card_id}"
        self.update_photo_card_image_url(photo_card_id, temp_url)
        return temp_url

    def update_photo_card_image_url(self, photo_card_id: int, image_url: str) -> None:
        """
        포토카드 이미지 url을 업데이트한다.
        :param photo_card_id: int 포토카드 id
        :param image_url: str 이미지 url
        """

        # celery를 사용하여 비동기로 처리 가능
        # 우선은 임시 동기처리
        PhotoCard.objects.filter(id=photo_card_id).update(image_url=image_url)
