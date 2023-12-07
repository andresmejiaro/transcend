import argparse
import asyncio
import websockets
import json

async def websocket_client(client_id, message_type, command, data):
    uri = f"ws://localhost:8000/ws/lobby/?client_id={client_id}"
    async with websockets.connect(uri) as websocket:
        message = {
            'type': message_type,
            'command': command,
            'data': data
        }
        await websocket.send(json.dumps(message))
        print(f"Sent message: {json.dumps(message)}")

        try:
            while True:
                response = await websocket.recv()
                print(f"Received response: {response}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")
        except KeyboardInterrupt:
            print("Manually interrupted. Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Client for LobbyConsumer testing")
    parser.add_argument("--client_id", type=int, required=True, help="Client ID for testing LobbyConsumer")
    parser.add_argument("--type", required=True, help="Message type")
    parser.add_argument("--command", required=True, help="Command")
    parser.add_argument("--data", default="{}", help="Data for the command")

    args = parser.parse_args()

    try:
        asyncio.get_event_loop().run_until_complete(
            websocket_client(args.client_id, args.type, args.command, json.loads(args.data))
        )
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C manually to avoid traceback
