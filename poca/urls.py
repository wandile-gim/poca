from django.urls import path

from poca.application.adapter.api.http import user_views, photo_card_views, photo_card_trade_views

urlpatterns = [
    # auth user views
    path('auth', user_views.login_view, name='login'),
    path('auth/register', user_views.register_view, name='register'),

    # photo card views
    path('cards', photo_card_views.PhotoCardAPIView.as_view(), name='photo_card_view'),
    path('sales', photo_card_trade_views.PhotoCardTradeAPIView.as_view(), name='photo_card_trade_view'),
    path('sales/<int:card_id>', photo_card_trade_views.PhotoCardDetailAPIView.as_view(),
         name='photo_card_trade_detail_view'),
    path('sales/min_price/<int:card_id>', photo_card_trade_views.PhotoCardMinPriceAPIView.as_view(),
         name='min_price_photo_card_trade_view'),
    path('purchase', photo_card_trade_views.PhotoCardPurchaseItemAPIView.as_view(),
         name='purchase_photo_card_trade_view'),
]
