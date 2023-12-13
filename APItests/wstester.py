import asyncio
import websockets
import json

async def websocket_client():
    try:
        tournament_id = input("Enter Tournament ID: ")
        client_id = input("Enter Client ID: ")
        command = input("Enter Command: ")
        data = input("Enter Data (JSON format): ")

        uri = f"ws://localhost:8000/ws/tournament/{tournament_id}/?client_id={client_id}"

        async with websockets.connect(uri) as websocket:
            message = {
                'command': command,
                'data': json.loads(data)
            }
            await websocket.send(json.dumps(message))
            print(f"Sent message: {json.dumps(message)}")

            try:
                while True:
                    response = await websocket.recv()
                    print(f"Received response: {response}")

                    try:
                        response_data = json.loads(response)
                        print(f"Response type: {response_data.get('type')}")
                        print(f"Response command: {response_data.get('command')}")
                        print(f"Response data: {response_data.get('data')}")

                        # Handle different response commands here
                        if response_data.get('command') == 'tournament_started':
                            print("Tournament has started!")

                    except json.JSONDecodeError:
                        print("Received non-JSON response.")

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")
                
    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(websocket_client())
    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")
