import os
from .userauth.jwt.sign import sign
from .userauth.jwt.verify import verify
from .userauth.jwt.decode import decode

from datetime import datetime, timedelta
    
    
secret_key = os.environ["JWT_SEED"]

def create_jwt_token(user_id, username, expiration_time_minutes=240):
    now = datetime.utcnow()
    expiration_time = now + timedelta(minutes=expiration_time_minutes)

    jwt_payload = {'user_id': user_id, 'username': username, 'exp': expiration_time.isoformat()}
    return sign(jwt_payload, secret_key)

def validate_and_get_user_from_token(token):
    try:
        payload = verify(token, secret_key)
        
        expiration_time_str = payload.get('exp')
        expiration_time = datetime.fromisoformat(expiration_time_str)
        
        if expiration_time < datetime.utcnow():
            raise Exception('Token has expired')

        user_id = payload.get('user_id')
        username = payload.get('username')
        
        from api.userauth.models import CustomUser
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise Exception('CustomUser not found')
        
        user_data = {
            'username': user.username,
            'fullname': user.fullname
        }

        return user_data

    except Exception as e:
        raise Exception(f'Token validation failed: {str(e)}')
    
def get_user_id_from_jwt_token(token):
    try:
        payload = verify(token, secret_key)

        expiration_time_str = payload.get('exp')
        expiration_time = datetime.fromisoformat(expiration_time_str)

        if expiration_time < datetime.utcnow():
            raise Exception('Token has expired')

        user_id = payload.get('user_id')

        return user_id

    except Exception as e:
        print(f'Token validation failed: {str(e)}')
        raise Exception(f'Token validation failed: {str(e)}')