from django.shortcuts import render
from django.http import JsonResponse
from ..models import CustomUser, Friendship
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
from api.jwt_utils import get_user_id_from_jwt_token
from .utils.validate_update import UserUpdateValidator
from django.shortcuts import get_object_or_404
from api.userauth.models import CustomUser
import magic


@requires_csrf_token
def info_me_view(request):
    if request.method == 'GET':
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                    user_id = get_user_id_from_jwt_token(token)
                    user = CustomUser.objects.get(id=user_id)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)

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
def update_avatar_view(request):
    try:
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                _, token = authorization_header.split()
                user_id = get_user_id_from_jwt_token(token)
                print(user_id)
                user = CustomUser.objects.get(id=user_id)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=401)
        if request.method == 'POST':
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']

                mime = magic.Magic(mime=True)
                mime_type = mime.from_buffer(avatar.read(1024))

                if not mime_type.startswith('image'):
                    return JsonResponse({'error': 'Invalid file format. Please upload a valid image.'}, status=400)

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


@requires_csrf_token
def user_friends_list(request):
    if request.method == 'GET':
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                    user_id = get_user_id_from_jwt_token(token)
                    user = CustomUser.objects.get(id=user_id)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)

            friendship = Friendship.objects.get(user=user)
            friends = friendship.friends.all()
            friend_list = []

            user_id_before_loop = user.id

            for friendship in friends:
                if friendship.id != user_id_before_loop:
                    friend_list.append({
                        'id': friendship.id,
                        'username': friendship.username,
                    })

            return JsonResponse({'status': 'ok', 'data': friend_list})

        except Friendship.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found or has no friends'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)


def update_user_information(request, *args, **kwargs):
    if request.method != 'PUT':
        return JsonResponse({"message": "Not allowed"}, status=405)
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return JsonResponse({"message": "Authorization header missing"}, status=401)
    try:
        _, token = authorization_header.split()
        user_id = get_user_id_from_jwt_token(token)
        user = CustomUser.objects.get(id=user_id)
    except Exception as e:
        return JsonResponse({'error': "Invalid token"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': "Invalid JSON"}, status=400)

    input_errors = UserUpdateValidator(data).validate()
    if input_errors:
        return JsonResponse({"message": "Something went wrong", "details": input_errors}, status=403)

    username = data.get("username")
    email = data.get("email")
    full_name = data.get("fullname")

    if username:
        user.username = username
    if email:
        user.email = email
    if full_name:
        user.fullname = full_name
    user.save()
    return JsonResponse({"message": "User updated successfully"}, status=200)



@requires_csrf_token
def info_user_view(request, username):
    if request.method == 'GET':
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)
            user = get_object_or_404(CustomUser, username=username)

            user_data_response = {
                'username': user.username,
                'fullname': user.fullname,
                'email': user.email,
                'avatar_url': user.avatar.url if user.avatar else None
            }
            return JsonResponse({'status': 'ok', 'user': user_data_response})

        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)
        except Exception as e:
            # Handle token validation failure
            return JsonResponse({'error': str(e)}, status=401)

    return JsonResponse({'error': 'Only GET requests are allowed'}, status=400)