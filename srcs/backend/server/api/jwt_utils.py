from .userauth.jwt.sign import sign
from .userauth.jwt.verify import verify
from .userauth.jwt.decode import decode
from .userauth.models import CustomUser
    
    
secret_key = 'hola'

def create_jwt_token(user_id, username):
    jwt_payload = {'user_id': user_id, 'username': username}

    return sign(jwt_payload, secret_key)

def validate_and_get_user_from_token(token):
    try:
        payload = verify(token, secret_key)

        user_id = payload.get('user_id')
        username = payload.get('username')

        user = CustomUser.objects.get(id=user_id, username=username)
        user_data = {
            'username': user.username,
            'fullname': user.fullname
        }

        return user_data

    except Exception as e:
        raise Exception(f'Token validation failed: {str(e)}')