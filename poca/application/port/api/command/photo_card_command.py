from dataclasses import dataclass


@dataclass
class CreatePhotoCardCommand:
    name: str
    description: str
    image_data: bytes
