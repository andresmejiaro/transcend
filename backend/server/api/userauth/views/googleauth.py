from django.shortcuts import render
from django.http import JsonResponse
from ..models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
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


def display_qr_code(request, user_id):
	user = CustomUser.objects.get(id=user_id)
	if not user.is_2fa_enabled:
		return JsonResponse({'message': '2FA is already disabled.'})
	secret_key = generate_secret_key()
	img_path = generate_qr_code(secret_key, user_id)
	save_secret_key_in_database(user_id, secret_key)
	return JsonResponse({'qrcode_path': img_path, 'user_id': user_id})

@requires_csrf_token
def enable_2fa(request, user_id):
	user = CustomUser.objects.get(id=user_id)
	if user.is_2fa_enabled:
		return JsonResponse({'message': '2FA is already enabled.'})

	secret_key = pyotp.random_base32()
	img_path = generate_qr_code(secret_key, user.id)
	user.enable_2fa(secret_key)
	return JsonResponse({'qrcode_path': img_path, 'message': 'Scan the QR code with your authenticator app to enable 2FA.'})

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
				user.is_2fa_setup_complete = True
				user.save()
				return JsonResponse({'status': 'ok', 'message': 'TOTP is valid'})
			else:
				return JsonResponse({'status': 'error', 'message': 'Invalid TOTP'})
		except CustomUser.DoesNotExist:
			return JsonResponse({'message': 'User not found'}, status=400)
		except pyotp.OTPError as e:
			return JsonResponse({'message': f'Error: {str(e)}'}, status=400)
	return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

@requires_csrf_token
def user_2fa_setup_complete(request, user_id):
	if request.method == 'GET':
		try:
			user = CustomUser.objects.get(id=user_id)
			if user.is_2fa_enabled and user.is_2fa_setup_complete:
				return JsonResponse({'status': True})
			return JsonResponse({'status': False})
		except CustomUser.DoesNotExist:
			return JsonResponse({'message': 'User not found'}, status=400)
	return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)
