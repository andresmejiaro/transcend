# middleware.py
from django.http import JsonResponse
from .jwt_utils import validate_and_get_user_from_token

# List of paths that should be excluded from token verification
EXCLUDED_PREFIXES = ['/api/user/login/', '/api/user/signup/', '/api/user/validate-jwt/', '/api/user/csrftoken/']

def should_exclude_path(request_path):
	return any(request_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)

def jwt_verification_middleware(get_response):
	def middleware(request):
		try:
			# Exclude certain paths from token verification
			if should_exclude_path(request.path):
				return get_response(request)

			# Extract and verify JWT from the request
			token = request.GET.get('token', '')
			if not validate_and_get_user_from_token(token):
				return JsonResponse({'error': 'Invalid token'}, status=401)

			# Continue with the request
			response = get_response(request)
			return response
		except Exception as e:
			# Handle token validation failure
			return JsonResponse({'error': str(e)}, status=401)

	return middleware
