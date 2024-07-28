from poca.application.adapter.api.http import user_views
from django.urls import path

urlpatterns = [
    path('auth', user_views.login_view, name='login'),

    path('auth/register', user_views.register_view, name='register'),
]

