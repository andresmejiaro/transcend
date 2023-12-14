import asyncio
import websockets
import json

async def websocket_client():
    try:
        tournament_id = input("Enter Tournament ID: ")
        client_id = input("Enter Client ID: ")

        uri = f"ws://localhost:8001/ws/tournament/{tournament_id}/?client_id={client_id}"

        # Connect to WebSocket
        websocket = await websockets.connect(uri)
        print(f"Connected to {uri}")

        try:
            while True:
                # Receive and print the response
                response = await websocket.recv()
                parsed_response = json.loads(response)
                formatted_response = json.dumps(parsed_response, indent=2)

                print(f"Received response:\n{formatted_response}")

                command = input("Enter Command: ").strip()
                data = input("Enter Data (JSON format): ").strip()
                message = {
                    'command': command,
                    'data': json.loads(data)
                }
                # Send message using the existing WebSocket connection
                await websocket.send(json.dumps(message))
                print(f"Sent message: {json.dumps(message)}")
        finally:
            await websocket.close()

    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")

if __name__ == "__main__":
    try:
        asyncio.run(websocket_client())

    except KeyboardInterrupt:
        print("Manually interrupted. Exiting...")