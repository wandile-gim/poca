import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from poca.application.adapter.spi.persistence.entity.user import User


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'status': 'error', 'message': 'Invalid request body'}, status=400)

        data = json.loads(request.body)
        user_email = data.get('user_email')
        password = data.get('password')

        if not user_email or not password:
            return JsonResponse({'status': 'error', 'message': 'Invalid request body'}, status=400)

        user = authenticate(request, user_email=user_email, password=password)
        if user is not None:
            login(request, user)
            response = JsonResponse({'status': 'success', 'message': 'Logged in successfully'})
            response.set_cookie('X-CSRFToken', get_token(request), httponly=True)
            return response
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'status': 'error', 'message': 'Invalid request body'}, status=400)

        data = json.loads(request.body)
        email = data.get('user_email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'status': 'error', 'message': 'Email and password are required'}, status=400)

        if User.objects.filter(user_email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email is already in use'}, status=400)

        user = User.objects.create_user(user_email=email, password=password)
        user.save()

        return JsonResponse({'status': 'success', 'message': 'User registered successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
