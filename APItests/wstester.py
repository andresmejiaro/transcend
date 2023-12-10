import asyncio
import websockets
import json

async def websocket_client():
    match_id = input("Enter Match ID: ")
    player_1_id = input("Enter Player 1 ID: ")
    player_2_id = input("Enter Player 2 ID: ")
    client_id = input("Enter Client ID: ")
    message_type = input("Enter Message Type: ")
    command = input("Enter Command: ")
    data = input("Enter Data (JSON format): ")

    uri = f"ws://localhost:8000/ws/pong/{match_id}/?player_1_id={player_1_id}&player_2_id={player_2_id}&client_id={client_id}"
    
    async with websockets.connect(uri) as websocket:
        message = {
            'type': message_type,
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
