from django.shortcuts import render
from django.http import JsonResponse
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from passlib.hash import pbkdf2_sha256
from django.middleware.csrf import get_token

def sendToken_view(request):
	csrf_token = get_token(request)
	return JsonResponse({'token': csrf_token})

def get_user_from_username(username):
	try:
		user = CustomUser.objects.get(username=username)
		return user
	except CustomUser.DoesNotExist:
		return None

@csrf_exempt
def get_user_by_username(request):
	if request.method == 'GET':
		try:
			data = json.loads(request.body.decode('utf-8'))
			username = data.get('username')
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


def signupIntra(request):
	pass

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

@csrf_exempt
def get_user_from_username_view(request, username):
	try:
		user = CustomUser.objects.get(username=username)
		user = {
			'username': user.username,
			'fullname': user.fullname
		}
		return JsonResponse({'user': user})
	except CustomUser.DoesNotExist:
		return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
def testView(request):
	return JsonResponse({'message': 'Test passed'})