"""
This file contains duplicate code because i was not able to import files from ../..
I am going to fix it later
"""
# TODO: see above

from datetime import datetime
import base64
import json
import hmac
import hashlib

secret_key = 'hola'  # TODO: Get from environment


def verify_signature(encoded_header, encoded_payload, signature, secret):
    data = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    expected_signature = hmac.new(secret.encode('utf-8'), data, hashlib.sha256)
    expected_signature = base64.urlsafe_b64encode(expected_signature.digest()).rstrip(b'=').decode('utf-8')

    return hmac.compare_digest(expected_signature.encode('utf-8'), signature.encode('utf-8'))

def verify(jwt, secret):
    encoded_header, encoded_payload, signature = jwt.split('.')

    if verify_signature(encoded_header, encoded_payload, signature, secret):
        # Remove any padding characters ('=') and decode the base64 strings
        encoded_header += '=' * ((4 - len(encoded_header) % 4) % 4)
        encoded_payload += '=' * ((4 - len(encoded_payload) % 4) % 4)

        header_bytes = base64.urlsafe_b64decode(encoded_header)
        payload_bytes = base64.urlsafe_b64decode(encoded_payload)

        header_str = header_bytes.decode('utf-8')
        payload_str = payload_bytes.decode('utf-8')

        header = json.loads(header_str)
        payload = json.loads(payload_str)
        return payload
    else:
        raise Exception('Invalid signature')


def verify(jwt, secret):
    encoded_header, encoded_payload, signature = jwt.split('.')

    if verify_signature(encoded_header, encoded_payload, signature, secret):
        # Remove any padding characters ('=') and decode the base64 strings
        encoded_header += '=' * ((4 - len(encoded_header) % 4) % 4)
        encoded_payload += '=' * ((4 - len(encoded_payload) % 4) % 4)

        header_bytes = base64.urlsafe_b64decode(encoded_header)
        payload_bytes = base64.urlsafe_b64decode(encoded_payload)

        header_str = header_bytes.decode('utf-8')
        payload_str = payload_bytes.decode('utf-8')

        header = json.loads(header_str)
        payload = json.loads(payload_str)

        return payload
    else:
        raise Exception('Invalid signature')



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
        raise Exception(f'Token validation failed: {str(e)}')
