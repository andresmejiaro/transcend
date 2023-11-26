from django.shortcuts import render
from django.http import JsonResponse
from ..models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.middleware.csrf import get_token
from ...jwt_utils import create_jwt_token, validate_and_get_user_from_token
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os




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


