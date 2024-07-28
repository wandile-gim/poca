from rest_framework import serializers

from poca.application.adapter.api.http.serializer.photo_card_serializer import PhotoCardSerializer


class PhotoCardTradeOnSaleListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    state = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=0)
    photo_card = PhotoCardSerializer()
