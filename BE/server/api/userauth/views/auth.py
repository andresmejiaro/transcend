from django.shortcuts import render
from django.http import JsonResponse
from ..models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from django.middleware.csrf import get_token
from ...jwt_utils import create_jwt_token, validate_and_get_user_from_token
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import pyotp
import qrcode


# AUTH
@csrf_exempt
@ensure_csrf_cookie
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            fullname = data.get('fullname')
            email = data.get('email')
            is_superuser = data.get('is_superuser')

            if not (username and password and fullname and email):
                return JsonResponse({"status": "error", "message": "Username, password, email or fullname is missing"}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)
            
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username already exists"}, status=400)

            user = CustomUser(username=username,
                              fullname=fullname, email=email)
            user.set_password(password)
            if is_superuser:
                user.is_superuser = True
            user.save()
            jwt_token = create_jwt_token(user.id, user.username)
            response = JsonResponse(
                {'status': 'ok', 'message': 'User created successfully', 'token': jwt_token})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

@csrf_exempt
@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = CustomUser.objects.get(username=username)
			
            if user.check_password(password):
                jwt_token = create_jwt_token(user.id, user.username)
                if user.is_2fa_enabled:
                    response = JsonResponse({'status': '2FA', 'message': 'Login successful', 'token': jwt_token})
                else:
                    response = JsonResponse({'status': 'ok', 'message': 'Login successful', 'token': jwt_token})
                response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

