from dependency_injector.wiring import Provide, inject
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from poca.application.adapter.api.http.serializer.photo_card_trade_deserializer import \
    RegisterPhotoCardTradeDeSerializer, BuyPhotoCardTradeDeSerializer
from poca.application.adapter.api.http.serializer.photo_card_trade_serializer import PhotoCardTradeOnSaleListSerializer, \
    PhotoCardTradeRecentlyTradeListSerializer
from poca.application.domain.model import photo_card_trade_result
from poca.application.domain.model.photo_card import OnSaleQueryStrategy
from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand
from poca.application.port.api.photo_card_trade_use_case import PhotoCardTradeUseCase


class PhotoCardTradeAPIView(APIView):
    use_case: PhotoCardTradeUseCase
    http_method_names = ['get', 'post']  # 리스트 조회, 판매 등록
    permission_classes = [IsAuthenticated]

    # 의존성 주입
    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def get(self, request):
        result = self.use_case.on_sale_photo_card(OnSaleQueryStrategy.MIN_PRICE_RENEWAL_LATE_FIRST)
        return self._build_response(result)

    def post(self, request):
        command = self._read_command(request)
        result = self.use_case.register_photo_card_on_sale(command)
        return self._build_response(result)

    # 서비스 로직의 반환 타입에 따라 response 객체 생성
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

    # request 데이터를 command 객체로 변환
    def _read_command(self, request) -> RegisterPhotoCardOnSaleCommand:
        serializer = RegisterPhotoCardTradeDeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return serializer.create()


class PhotoCardDetailAPIView(APIView):
    use_case: PhotoCardTradeUseCase
    http_method_names = ['get']  # 최근 판매된 포토카드 조회
    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def get(self, request, card_id: int):
        result = self.use_case.get_recently_sold_photo_card(card_id=card_id)
        return self._build_response(result)

    def _build_response(self, result: photo_card_trade_result.PhotoCardTradeResult) -> Response:
        response = None
        match result:
            case photo_card_trade_result.NoPhotoCardOnSaleResult():
                response = Response(data={"message": result.to_message()}, status=404)
            case photo_card_trade_result.PhotoCardTradeRecentlySoldResult():
                data = PhotoCardTradeRecentlyTradeListSerializer(result).data
                response = Response(data=data, status=200)

        return response


class PhotoCardMinPriceAPIView(APIView):
    use_case: PhotoCardTradeUseCase
    http_method_names = ['get']  # 최저 가격 포토카드 조회
    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def get(self, request, card_id: int):
        result = self.use_case.get_min_price_photo_card_on_sale(card_id=card_id)
        return self._build_response(result)

    def _build_response(self, result: photo_card_trade_result.PhotoCardTradeResult) -> Response:
        response = None
        match result:
            case photo_card_trade_result.NoPhotoCardOnSaleResult():
                response = Response(data=result.to_message(), status=404)
            case photo_card_trade_result.PhotoCardTradeResultObject():
                data = PhotoCardTradeOnSaleListSerializer(result.record).data
                response = Response(data=data, status=200)

        return response


class PhotoCardPurchaseItemAPIView(APIView):
    """
    포토카드 구매 API View
    """
    use_case: PhotoCardTradeUseCase
    http_method_names = ['post']  # 아이템 구매
    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self,
                 photo_card_trade_use_case: PhotoCardTradeUseCase = Provide["photo_card_trade_use_case"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_case = photo_card_trade_use_case

    def post(self, request):
        command = self._read_command(request)
        result = self.use_case.buy_photo_card_on_record(record_id=command['record_id'], buyer_id=command['buyer_id'])
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
