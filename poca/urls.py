from poca.application.adapter.api.http import user_views, photo_card_views, photo_card_trade_views
from django.urls import path

urlpatterns = [
    # auth user views
    path('auth', user_views.login_view, name='login'),
    path('auth/register', user_views.register_view, name='register'),

    # photo card views
    path('sales', photo_card_trade_views.PhotoCardTradeAPIView.as_view(), name='photo_card_trade_view'),
    path('cards', photo_card_views.PhotoCardAPIView.as_view(), name='photo_card_view'),
    path('sales/<int:trade_id>', photo_card_trade_views.PhotoCardTradeItemAPIView.as_view(), name='photo_card_trade_view'),
    path('sales/<int:trade_id>', photo_card_trade_views.PhotoCardTradeItemAPIView.as_view(), name='photo_card_view'),
]

