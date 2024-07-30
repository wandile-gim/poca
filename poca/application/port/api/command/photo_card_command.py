from dataclasses import dataclass


@dataclass
class CreatePhotoCardCommand:
    """
    사진 카드 등록을 위한 시그니처 클래스
    """
    name: str
    description: str
    image_data: bytes
