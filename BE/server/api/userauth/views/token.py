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


# ESTE ENDPOINT NO DEBERIA EXISTIR
@csrf_exempt
def send_csrf_token_view(request):
    csrf_token = get_token(request)
    response = JsonResponse({'token': csrf_token})
    return response


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
