from rest_framework import serializers

from poca.application.port.api.command.photo_card_trade_command import RegisterPhotoCardOnSaleCommand


class RegisterPhotoCardTradeDeSerializer(serializers.Serializer[RegisterPhotoCardOnSaleCommand]):
    card_id = serializers.IntegerField()
    seller_id = serializers.IntegerField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=0)
    fee = serializers.DecimalField(max_digits=10, decimal_places=0)

    def create(self) -> RegisterPhotoCardOnSaleCommand:
        validated_data = self.validated_data
        validated_data['seller_id'] = self.context['request'].user.id

        return RegisterPhotoCardOnSaleCommand(**self.validated_data)


class BuyPhotoCardTradeDeSerializer(serializers.Serializer):
    buyer_id = serializers.IntegerField(required=False)
    record_id = serializers.IntegerField()

    def create(self):
        validated_data = self.validated_data
        validated_data['buyer_id'] = self.context['request'].user.id

        return validated_data
