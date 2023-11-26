from django.shortcuts import render
from django.http import JsonResponse
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.middleware.csrf import get_token
from ..jwt_utils import create_jwt_token, validate_and_get_user_from_token
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import pyotp
import qrcode


# AUTH
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

# TOKENS
@csrf_exempt
def send_csrf_token_view(request):
    csrf_token = get_token(request)
    response = JsonResponse({'token': csrf_token})
    return response


@csrf_exempt
def validate_jwt_token_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            token = validate_and_get_user_from_token(token)
            return JsonResponse(token)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)



# USER HANDLILNG & CRUD
@csrf_exempt
def info_me_view(request, username):
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(username=username)
            user_data_response = {
                'username': user.username,
                'fullname': user.fullname,
                'email': user.email,
                'avatar_url': user.avatar.url if user.avatar else None
            }
            return JsonResponse({'status': 'ok', 'user': user_data_response})

        except Exception as e:
            # Handle token validation failure
            return JsonResponse({'error': str(e)}, status=401)

    return JsonResponse({'error': 'Only GET requests are allowed'}, status=400)


@csrf_exempt
def update_avatar_view(request, username):
    try:
        user = CustomUser.objects.get(username=username)

        if request.method == 'POST':
            if 'avatar' not in request.FILES:
                return JsonResponse({'error': 'Missing avatar in files'}, status=400)

            avatar = request.FILES['avatar']

            # Check if the uploaded file is an image
            if not avatar.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                return JsonResponse({'error': 'Invalid file format. Please upload a valid image.'}, status=400)

            # Check if the uploaded file is too large
            if avatar.size > 10 * 1024 * 1024:  # 10 MB
                return JsonResponse({'error': 'File size exceeds the limit. Please upload a smaller image.'}, status=400)

            filename, extension = os.path.splitext(avatar.name)
            count = 1
            while default_storage.exists(os.path.join('avatars', f'{filename}_{count}{extension}')):
                count += 1
            unique_filename = f'{filename}_{count}{extension}'
            user.avatar.save(unique_filename, ContentFile(avatar.read()))
            # user.update_avatar(avatar)
            return JsonResponse({'status': 'ok', 'message': 'Avatar updated successfully'})
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_user_from_username(username):
	try:
		user = CustomUser.objects.get(username=username)
		return user
	except CustomUser.DoesNotExist:
		return None

@csrf_exempt
def get_user_id(request, username):
    if request.method == 'GET':
        try:
            if username:
                user = get_user_from_username(username)
                if user:
                    return JsonResponse({'user_id': user.id, 'username': user.username})
                else:
                    return JsonResponse({'message': 'User not found'}, status=404)
            else:
                return JsonResponse({'message': 'Username missing in the request body'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON in the request body'}, status=400)

    return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)


# 2FA -------
def generate_secret_key():
    return pyotp.random_base32()


def generate_qr_code(secret_key, user_id):
    totp = pyotp.TOTP(secret_key)
    uri = totp.provisioning_uri(
        name=f"user_{user_id}", issuer_name="Pixel Pong")
    img = qrcode.make(uri)
    img_path = f'static/qrcode_{user_id}.png'
    img.save(img_path)
    return img_path


def save_secret_key_in_database(user_id, secret_key):
    user_profile, created = CustomUser.objects.get_or_create(
        id=user_id, defaults={'secret_key': secret_key})
    if not created:
        user_profile.secret_key = secret_key
        user_profile.save()


def get_secret_key_from_database(user_id):
    user_profile = CustomUser.objects.get(id=user_id)
    return user_profile.secret_key


@csrf_exempt
def display_qr_code(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if not user.is_2fa_enabled:
        return JsonResponse({'message': '2FA is already disabled.'})
    secret_key = generate_secret_key()
    img_path = generate_qr_code(secret_key, user_id)
    save_secret_key_in_database(user_id, secret_key)
    return JsonResponse({'qrcode_path': img_path, 'user_id': user_id})


@csrf_exempt
def enable_2fa(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if user.is_2fa_enabled:
        return JsonResponse({'message': '2FA is already enabled.'})

    secret_key = pyotp.random_base32()
    img_path = generate_qr_code(secret_key, user.id)
    user.enable_2fa(secret_key)
    return JsonResponse({'qrcode_path': img_path, 'message': 'Scan the QR code with your authenticator app to enable 2FA.'})


@csrf_exempt
def disable_2fa(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if not user.is_2fa_enabled:
        return JsonResponse({'message': '2FA is already disabled.'})
    user.disable_2fa()
    return JsonResponse({'message': '2FA has been disabled.'})


@csrf_exempt
def verify_totp_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            totp_code = data.get('totp_code')
            
            user = CustomUser.objects.get(id=user_id)

            if not user.is_2fa_enabled:
                return JsonResponse({'message': '2FA is not enabled for this user.'}, status=400)

            totp = pyotp.TOTP(user.secret_key)
            is_valid = totp.verify(totp_code)

            if is_valid:
                return JsonResponse({'message': 'TOTP is valid'})
            else:
                return JsonResponse({'message': 'Invalid TOTP'}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=400)
        except pyotp.OTPError as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

