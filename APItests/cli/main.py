# main.py

import asyncio
import websockets
from http_api import http_api
from websocket_api import websocket_api

api_client = http_api()
websocket_manager = websocket_api()

# Global variable to control the infinite loops
keep_running = True

async def handle_lobby_websocket(websocket):
    global keep_running
    try:
        while keep_running:
            data = await websocket_manager.receive(websocket)
            if data:
                print(data)

    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket_manager.close(websocket)

async def clean_close():
    # Close all WebSocket connections
    await websocket_manager.close_all()

async def main():
    try:
        global keep_running
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # Create a new user
        api_client.login(username, password)
        
        lobby_websocket = await websocket_manager.connect("ws://localhost:8001/ws/lobby2/", {"client_id": api_client.client_id})
        websocket_task = asyncio.create_task(handle_lobby_websocket(lobby_websocket))

        while keep_running:
            print("Waiting for messages...")
            await asyncio.sleep(1)


    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Ctrl+C pressed. Cleaning up...")
        keep_running = False  # Set the flag to False to stop all the infinite loops
    finally:
        # Wait for cleanup
        await asyncio.gather(clean_close(), websocket_task, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Suppress the second KeyboardInterrupt error during exit
    finally:
        print("Exiting...")
