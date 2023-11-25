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

            user = CustomUser(username=username, fullname=fullname, email=email)
            user.set_password(password)
            if is_superuser:
                user.is_superuser = True
            user.save()
            jwt_token = create_jwt_token(user.id, user.username)
            response = JsonResponse({'status': 'ok', 'message': 'User created successfully', 'token': jwt_token})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)


def signupIntra(request):
	pass

def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = CustomUser.objects.get(username=username)
			
            if user.check_password(password):
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

def info_me_jwt_view(request):
    if request.method == 'GET':
        try:
            username = request.GET.get('username', '')
            user = CustomUser.objects.get(username=username)
            user_data_response = {
                'username': user.username,
                'fullname': user.fullname
            }
            return JsonResponse({'status': 'ok', 'user': user_data_response})

        except Exception as e:
            # Handle token validation failure
            return JsonResponse({'error': str(e)}, status=401)

    return JsonResponse({'error': 'Only GET requests are allowed'}, status=400)

@csrf_exempt
def info_me_view(request):
    if request.method == 'GET':
        try:
            username = request.GET.get('username', '')
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

# def update_avatar_view(request, username):
#     print(request.FILES)  # Print files received in the request
#     try:
#         user = CustomUser.objects.get(username=username)
#         if request.method == 'POST' and 'avatar' in request.FILES:
#             avatar = request.FILES['avatar']
#             print(avatar.name)  # Print the name of the received file
#             user.update_avatar(avatar)
#             return JsonResponse({'status': 'ok', 'message': 'Avatar updated successfully'})
#         else:
#             return JsonResponse({'error': 'Invalid request or missing avatar'}, status=400)
#     except CustomUser.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)

# def get_user_from_username_view(request, username):
#     if request.method == 'GET':
#         try:
#             token = request.GET.get('token', '')
#             user_data = validate_and_get_user_from_token(token)
#             return JsonResponse({'user': user_data})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=401)

#     return JsonResponse({'error': 'Only GET requests are allowed'}, status=400)

# def get_user_from_username(username):
# 	try:
# 		user = CustomUser.objects.get(username=username)
# 		return user
# 	except CustomUser.DoesNotExist:
# 		return None

# @csrf_exempt
# def get_user_by_username(request):
# 	if request.method == 'GET':
# 		try:
# 			data = json.loads(request.body.decode('utf-8'))
# 			username = data.get('username')
# 			if username:
# 				user = get_user_from_username(username)
# 				if user:
# 					return JsonResponse({'user_id': user.id, 'username': user.username})
# 				else:
# 					return JsonResponse({'message': 'User not found'}, status=404)
# 			else:
# 				return JsonResponse({'message': 'Username missing in the request body'}, status=400)

# 		except json.JSONDecodeError:
# 			return JsonResponse({'message': 'Invalid JSON in the request body'}, status=400)

# 	return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)
