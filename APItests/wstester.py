import argparse
import json
import threading
import websocket
import time

class WebSocketClient:
    def __init__(self, ws_url, on_message_callback, on_ping_callback=None):
        self.ws = websocket.WebSocketApp(ws_url, on_message=on_message_callback)
        self.ws.on_ping = on_ping_callback

        # Start a separate thread for WebSocket communication
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.start()

    def send_message(self, action, data):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            message = {
                'type': action,
                'data': data,
            }
            self.ws.send(json.dumps(message))
            print(f"Sent message: {message}")
        else:
            print("WebSocket connection is closed.")

    def close(self):
        self.ws.close()
        self.ws_thread.join()

def on_ping(ws, message):
    print(f"Received Ping")
    ws.send(json.dumps({
        "type": "ping",
        "data": {
            "message": "pong"
        }
    }))

def on_message(ws, message):
    print(f"Received message: {message}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="WebSocket Test Script")
    parser.add_argument("--client_id", required=True, help="client_id for the WebSocket connection")
    args = parser.parse_args()

    # Use a fixed URL without room parameter
    ws_url = f"ws://127.0.0.1:8000/ws/lobby/?client_id={args.client_id}"

    # Create an instance of WebSocketClient
    ws_client = WebSocketClient(ws_url, on_message, on_ping)

    try:
        # Add a delay to allow time for the WebSocket connection to be established
        time.sleep(2)  # You might need to adjust the duration based on your server setup

        # Send a get_list_users action to the server every 10 seconds
        while True:
            ws_client.send_message('get_list_users', '')
            time.sleep(10)

    except KeyboardInterrupt:
        # Handle Ctrl+C to gracefully stop the program
        ws_client.close()
