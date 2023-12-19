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
from django.utils.text import slugify
from urllib import request as urllib_request
from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
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

@requires_csrf_token
def info_me_id_view(request, user_id):
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(pk=user_id)
            user_data_response = {
                'username': user.username,
                'fullname': user.fullname,
                'avatar_url': user.avatar.url if user.avatar else None
            }
            return JsonResponse({'status': 'ok', 'user': user_data_response})

        except Exception as e:
            # Handle token validation failure
            return JsonResponse({'error': str(e)}, status=401)

    return JsonResponse({'error': 'Only GET requests are allowed'}, status=400)


@requires_csrf_token
def update_avatar_view(request, username):
    try:
        user = CustomUser.objects.get(username=username)
        if request.method == 'POST':
            if 'avatar' in request.FILES:
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
                # user.avatar.save(unique_filename, ContentFile(avatar.read()))
                user.update_avatar(avatar)
                return JsonResponse({'status': 'ok', 'message': 'Avatar updated successfully'})

            elif json.loads(request.body).get('avatar_url'):
                # Handle image URL
                avatar_url = json.loads(request.body).get('avatar_url')

                try:
                    # Download the image from the URL using urllib
                    with urllib_request.urlopen(avatar_url) as response:
                        image_data = response.read()

                    # Check if the downloaded content is an image
                    content_type = response.getheader('Content-Type').lower()
                    if 'image' not in content_type:
                        return JsonResponse({'error': 'Invalid content type. Please provide a valid image URL.'}, status=400)

                    # Create a filename from the URL
                    filename = slugify(os.path.basename(avatar_url))
                    _, extension = os.path.splitext(filename)
                    count = 1
                    while default_storage.exists(os.path.join('avatars', f'{filename}_{count}{extension}')):
                        count += 1
                    unique_filename = f'{filename}_{count}{extension}'

                    # Save the image to the avatar field
                    user.avatar.save(unique_filename, ContentFile(image_data))
                    return JsonResponse({'status': 'ok', 'message': 'Avatar updated successfully'})

                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=400)
            else:
                return JsonResponse({'error': 'Missing avatar or avatar_url in request'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'err': str(e)}, status=400)

def get_user_from_username(username):
	try:
		user = CustomUser.objects.get(username=username)
		return user
	except CustomUser.DoesNotExist:
		return None

@requires_csrf_token
def get_user_id(request, username):
    if request.method == 'GET':
        try:
            if username:
                user = get_user_from_username(username)
                if user:
                    return JsonResponse({'user_id': user.id, 'username': user.username})
                else:
                    return JsonResponse({'message': 'User not found'})
            else:
                return JsonResponse({'message': 'Username missing in the request body'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON in the request body'}, status=400)

    return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)

@csrf_exempt
def user_exists(request, username):
    try:
        user = CustomUser.objects.get(username=username)
        return JsonResponse({"status": "exists"})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "no user found"})

@csrf_exempt
def user_intra_exists(request, username, fullname):
    try:
        user = CustomUser.objects.get(username=username, fullname=fullname)
        return JsonResponse({"status": "exists"})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "no user found"})

