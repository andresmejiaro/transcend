import asyncio
import websockets
import json
import threading  # Add this import

async def connect_and_listen(uri):
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

def websocket_client():
    try:
        tournament_id = input("Enter Tournament ID: ")
        client_id = input("Enter Client ID: ")

        uri = f"ws://localhost:8001/ws/tournament/{tournament_id}/?client_id={client_id}"

        # for lobbyconsumer
        # uri = f'ws://localhost:8001/ws/lobby/?client_id={client_id}'

        # Run the WebSocket listening part in a separate thread
        listen_thread = threading.Thread(target=asyncio.run, args=(connect_and_listen(uri),))
        listen_thread.start()

        while True:
            command = input("Enter Command: ")
            data = input("Enter Data (JSON format): ")

            message = {
                'command': command,
                'data': json.loads(data)
            }
            asyncio.run(websocket_send(uri, message))
            print(f"Sent message: {json.dumps(message)}")

    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")

async def websocket_send(uri, message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(message))

if __name__ == "__main__":
    try:
        websocket_client()
    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")
