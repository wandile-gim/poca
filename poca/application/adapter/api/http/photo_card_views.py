from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from poca.application.adapter.spi.persistence.repository.photo_card_repository import PhotoCardRepository
from poca.application.port.api.command.photo_card_command import CreatePhotoCardCommand


class PhotoCardAPIView(APIView):
    """
    PhotoCardTradeAPIView는 PhotoCardTradeUseCase를 사용하여 판매중인 포토카드 목록을 조회하는 APIView입니다.
    """
    http_method_names = ['get', 'post']  # 리스트 조회, 판매 등록
    permission_classes = [IsAuthenticated]

    def business_logic(self, cmd: CreatePhotoCardCommand):
        """
        포토카드 등록 비즈니스 로직을 수행합니다.
        :param cmd: CreatePhotoCardCommand 포토카드 등록 명령
        :info 이미지 업로드는 celery를 사용하여 비동기로 처리할 수 있습니다.
        """
        repo = PhotoCardRepository()

        # todo: 이미지 업로드는 async로 처리
        repo.register_new_photo_card(cmd)

    def post(self, request):
        """
        판매할 포토카드를 등록합니다.
        """

        name = request.data.get('name')
        description = request.data.get('description')
        image_file = request.data.get('image_file')

        if not name or not description or not image_file:
            return Response({'status': 'error', 'message': 'All fields are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        image_data = image_file.read()

        cmd = CreatePhotoCardCommand(
            name=request.data['name'],
            description=request.data['description'],
            image_data=image_data,
        )

        self.business_logic(cmd)
        return Response({'status': 'success', 'message': 'Photo card registered successfully'},
                        status=status.HTTP_201_CREATED)
