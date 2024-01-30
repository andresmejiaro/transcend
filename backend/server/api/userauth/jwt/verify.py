# jwt/verify.py
import json
import base64
import hmac
import hashlib

def verify_signature(encoded_header, encoded_payload, signature, secret):
    data = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    expected_signature = hmac.new(secret.encode('utf-8'), data, hashlib.sha256)
    expected_signature = base64.urlsafe_b64encode(expected_signature.digest()).rstrip(b'=').decode('utf-8')

    return hmac.compare_digest(expected_signature.encode('utf-8'), signature.encode('utf-8'))

def verify(jwt, secret):
    encoded_header, encoded_payload, signature = jwt.split('.')

    if verify_signature(encoded_header, encoded_payload, signature, secret):
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


