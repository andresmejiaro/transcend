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
from django.http import HttpResponseRedirect
from django.conf import settings
import requests
from ..oauth.user_info import get_user_info, get_or_create_user_oauth



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

            if len(username) > 20 or len(fullname) > 20:
                return JsonResponse({"status": "error", "message": "Username or full name too long."}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)

            if email.endswith("student.42madrid.com"):
                return JsonResponse({"status": "error", "message": "Email can not be from 42madrid."}, status=400)

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
                if user.is_2fa_enabled and user.is_2fa_setup_complete:
                    response = JsonResponse({'status': '2FA', 'message': 'Login successful', 'user_id': user.id})
                else:
                    jwt_token = create_jwt_token(user.id, user.username)
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


@csrf_exempt
@ensure_csrf_cookie
def oauth_start(request, *args, **kwargs):
    client_id = os.getenv("INTRA_CLIENT_ID")
    redirect_uri = os.getenv("INTRA_REDIRECT_URI")
    oauth_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    
    response = JsonResponse({'status': 'ok', 'url': oauth_url})
    response['Access-Control-Allow-Methods'] = '*'
    response['Access-Control-Allow-Headers'] = '*'

    return response


@csrf_exempt
@ensure_csrf_cookie
def oauth_login(request, *args, **kwargs):
    if request.method == "POST":
        data = json.loads(request.body)
        code = data.get("code")
        if not code:
            return JsonResponse({"detail": "No code provided"}, status=400)

        data = {
            "client_id": os.getenv("INTRA_CLIENT_ID"),
            "client_secret": os.getenv("INTRA_CLIENT_SECRET"),
            "redirect_uri": os.getenv("INTRA_REDIRECT_URI"),
            "grant_type": "authorization_code",
            "code": code,
        }

        oauth_url = "https://api.intra.42.fr/oauth/token/"

        response = requests.post(oauth_url, json=data)
        if response.status_code != 200:
            return JsonResponse({"detail": "Invalid code"}, status=401)

        access_token = response.json().get("access_token")
        user_info = get_user_info(access_token)

        user = get_or_create_user_oauth(user_info)
        jwt_token = create_jwt_token(user.id, user.username)

        return JsonResponse({"token": jwt_token})

    return JsonResponse({
        "detail": "Method not allowed",
        "status": 405
    })