# jwt/sign.py
import json
import base64
import hmac
import hashlib

def create_signature(encoded_header, encoded_payload, secret):
    data = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), data, hashlib.sha256)
    return base64.urlsafe_b64encode(signature.digest()).rstrip(b'=').decode('utf-8')

def sign(payload, secret):
    header = {"alg": "HS256", "typ": "JWT"}

    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).rstrip(b'=').decode('utf-8')
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).rstrip(b'=').decode('utf-8')

    signature = create_signature(encoded_header, encoded_payload, secret)

    return f"{encoded_header}.{encoded_payload}.{signature}"
