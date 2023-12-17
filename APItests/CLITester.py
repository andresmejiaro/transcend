import json
import asyncio
import websockets
import os

# Define the WebSocket URI template
uri_template = "ws://localhost:8001/ws/pong/{matchId}/?player_1_id={player1Id}&player_2_id={player2Id}&client_id={clientId}&scorelimit={scoreLimit}"

# Function to clear the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def start_game(uri, match_id, player1_id, player2_id, client_id, score_limit):
    uri = uri.format(matchId=match_id, player1Id=player1_id, player2Id=player2_id, clientId=client_id, scoreLimit=score_limit)
    async with websockets.connect(uri) as ws:
        print("WebSocket connection opened.")
        while True:
            try:
                data = await ws.recv()
                data = json.loads(data)
                print("Received message:", data)
                update_game_canvas(data)
            except websockets.ConnectionClosed:
                print("WebSocket connection closed.")
                break

def send_json(ws, json_message):
    print("WebSocket readyState:", ws.state)
    if ws.state == websockets.State.OPEN:
        ws.send(json.dumps(json_message))
        print("Sent JSON message:", json.dumps(json_message))
    else:
        print("WebSocket connection not open.")

def update_game_canvas(data):
    print("Updating game canvas with data:", data)

    if data["type"] == "player_list":
        # Handle player list data if needed
        print("Received player list:", data["data"])
    elif data["type"] == "game_update":
        # Handle game update data
        draw_pong_game(data["data"])
    elif data["type"] == "update_buffer":
        # Handle buffered game updates
        for update in data["data"]:
            print("Buffered game update:", update)
            draw_pong_game(update["game_update"])
    else:
        print("Invalid message type:", data["type"])

def draw_pong_game(data):
    # Check if the required properties exist in the data object
    if (
        data and
        data["ball"] and
        data["leftPaddle"] and
        data["rightPaddle"]
    ):
        clear_screen()

        # Draw only if the ball, leftPaddle, and rightPaddle properties are present
        draw_rect(data["ball"]["position"], data["ball"]["size"], "blue")
        draw_rect(data["leftPaddle"]["position"], data["leftPaddle"]["size"], "green")
        draw_rect(data["rightPaddle"]["position"], data["rightPaddle"]["size"], "red")

        scores = data["score"]
        print(f"{data['player1Id']}: {scores[data['player1Id']]} - {data['player2Id']}: {scores[data['player2Id']]}")
    else:
        print("Invalid data format:", data)

def draw_rect(position, size, color):
    # Simple terminal-based rectangle drawing
    # Note: This is a very basic implementation, and you might need to improve it based on your needs.
    print(f"\033[48;5;{color_map[color]}m{' ' * size['x']}")  # Use ANSI escape codes for colored backgrounds

# Color mapping for ANSI escape codes
color_map = {
    "blue": 21,
    "green": 46,
    "red": 196,
}

# Example usage
async def main():
    match_id = "your_match_id"
    player1_id = "your_player1_id"
    player2_id = "your_player2_id"
    client_id = "your_client_id"
    score_limit = 11

    uri = uri_template  # Use the global template
    await start_game(uri, match_id, player1_id, player2_id, client_id, score_limit)

if __name__ == "__main__":
    asyncio.run(main())
