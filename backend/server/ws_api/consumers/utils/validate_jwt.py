from datetime import datetime
import os

from api.userauth.jwt.verify import verify

secret_key = os.environ["JWT_SEED"]


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
