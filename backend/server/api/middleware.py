# middleware.py
from django.http import JsonResponse
from .jwt_utils import validate_and_get_user_from_token
import logging

# List of paths that should be excluded from token verification
EXCLUDED_PREFIXES = ['/api/test/', '/api/user/login/', '/api/user/signup/', '/api/user/validate-jwt/', '/media/', '/api/user/exists/', '/pong/', '/admin/', '/api/verify_totp_code/', '/api/oauth-init/', '/api/oauth/login/']

def should_exclude_path(request_path):
	return any(request_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


logger = logging.getLogger(__name__)
def jwt_verification_middleware(get_response):
    def middleware(request):
        try:
            if should_exclude_path(request.path):
                return get_response(request)

            authorization_header = request.headers.get('Authorization', '')
            if authorization_header.startswith('Bearer '):
                token = authorization_header[len('Bearer '):].strip()
            else:
                logger.warning('JWT token not found in the Authorization header')
                return JsonResponse({'error': 'JWT token not found in the Authorization header'}, status=401)

            if not validate_and_get_user_from_token(token):
                logger.warning('Invalid token')
                return JsonResponse({'error': 'Invalid token'}, status=401)

            response = get_response(request)
            return response

        except Exception as e:
            logger.error(f'Token verification failed: {str(e)}')
            return JsonResponse({'error': str(e)}, status=401)

    return middleware
