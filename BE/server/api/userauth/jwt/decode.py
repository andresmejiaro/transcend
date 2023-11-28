# jwt/decode.py
import json
import base64

def decode(jwt):
    encoded_header, encoded_payload, _ = jwt.split('.')

    return {
        'header': json.loads(base64.urlsafe_b64decode(encoded_header + b'=').decode('utf-8')),
        'payload': json.loads(base64.urlsafe_b64decode(encoded_payload + b'=').decode('utf-8')),
    }
      