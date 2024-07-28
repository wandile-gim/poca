from dependency_injector.wiring import Provide, inject
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from poca.application.adapter.api.http.serializer.photo_card_trade_deserializer import \
    RegisterPhotoCardTradeDeSerializer, BuyPhotoCardTradeDeSerializer
from poca.application.adapter.api.http.serializer.photo_card_trade_serializer import PhotoCardTradeOnSaleListSerializer
from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import OnSaleQueryStrategy
from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand
from poca.application.port.api.photo_card_trade_use_case import PhotoCardTradeUseCase


class PhotoCardTradeAPIView(APIView):
    use_case: PhotoCardTradeUseCase
    http_method_names = ['get', 'post']  # 리스트 조회, 판매 등록
    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def get(self, request):
        result = self.use_case.on_sale_photo_card(OnSaleQueryStrategy.MIN_PRICE_RENEWAL_LATE_FIRST.value)
        return self._build_response(result)

    def post(self, request):
        command = self._read_command(request)
        result = self.use_case.register_photo_card_on_sale(command)
        return self._build_response(result)

    def _build_response(self, result: photo_card_trade_result.PhotoCardTradeResult) -> Response:
        response = None
        match result:
            case list():
                data = PhotoCardTradeOnSaleListSerializer(result, many=True).data
                response = Response(data=data, status=200)
            case photo_card_trade_result.PhotoCardSaleRegisterFailResult():
                response = Response(data={"message": result.to_message()}, status=400)
            case photo_card_trade_result.PhotoCardSaleRegisteredResult():
                response = Response(data={"message": result.to_message()}, status=201)

        return response

    def _read_command(self, request) -> RegisterPhotoCardOnSaleCommand:
        serializer = RegisterPhotoCardTradeDeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return serializer.create()


class PhotoCardTradeItemAPIView(APIView):
    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def post(self, request, trade_id: int):
        command = self._read_command(request)
        result = self.use_case.buy_photo_card_on_record(record_id=trade_id, buyer_id=command['buyer_id'])
        return self._build_response(result)

    def _build_response(self, result: photo_card_trade_result.PhotoCardTradeResult) -> Response:
        response = None
        match result:
            case photo_card_trade_result.InsufficientBalanceResult():
                response = Response(data={"message": result.to_message()}, status=status.HTTP_406_NOT_ACCEPTABLE)
            case photo_card_trade_result.NoPhotoCardOnSaleResult():
                response = Response(data={"message": result.to_message()}, status=status.HTTP_417_EXPECTATION_FAILED)
            case photo_card_trade_result.PhotoCardTradeProcessedResult():
                response = Response(data={"message": result.to_message()}, status=status.HTTP_200_OK)
            case photo_card_trade_result.PhotoCardTradeNotProcessedResult():
                response = Response(data={"message": result.to_message()}, status=status.HTTP_409_CONFLICT)

        return response

    #
    def _read_command(self, request) -> dict:
        serializer = BuyPhotoCardTradeDeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return serializer.create()
