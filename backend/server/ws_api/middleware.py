from django.http import JsonResponse
from channels.middleware import BaseMiddleware

# class WebSocketCompressionMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         try:
#             if b"websocket" in scope.get("subprotocols", b""):
#                 # Check if the WebSocket handshake request contains the 'Sec-WebSocket-Extensions' header
#                 extensions_header = scope.get('headers', {}).get(b'sec-websocket-extensions', b'')

#                 if b'permessage-deflate' in extensions_header:
#                     # Compression is already negotiated, proceed with the WebSocket connection
#                     return await super().__call__(scope, receive, send)

#                 # Compression is not negotiated, add the extension to the response headers
#                 response_headers = [
#                     (b"Sec-WebSocket-Extensions", b"permessage-deflate"),
#                 ]

#                 # Send the modified headers to the client
#                 await send({
#                     "type": "websocket.accept",
#                     "headers": response_headers,
#                 })

#                 # Continue with the WebSocket connection
#                 return await super().__call__(scope, receive, send)

#             # Not a WebSocket connection, continue with the next middleware or consumer
#             return await super().__call__(scope, receive, send)

#         except Exception as e:
#             response = JsonResponse({'error': str(e)}, status=401)
#             await send({
#                 "type": "websocket.close",
#                 "code": 4000,
#             })
#             return response