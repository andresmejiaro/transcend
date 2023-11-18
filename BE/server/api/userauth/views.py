from django.shortcuts import render
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json

# Create your views here.
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            fullname = data.get('fullname')

            if not (username and password and fullname):
                return JsonResponse({"status": "error", "message": "Username, password, or fullname is missing"}, status=400)

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username already exists"}, status=400)

            user = CustomUser(username=username, fullname=fullname)
            user.set_password(password)
            user.save()

            response = JsonResponse({'status': 'ok', 'message': 'User created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = CustomUser.objects.get(username=username)
			
            response = JsonResponse({'status': 'ok', 'message': 'Login successful'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            if user.check_password(password):
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