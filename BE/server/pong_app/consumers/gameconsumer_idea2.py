import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
import asyncio

# Constants for the game window dimensions
WALL_WIDTH = 800  # Adjust this based on your actual game window width
WALL_HEIGHT = 600  # Adjust this based on your actual game window height

class Ball:
    def __init__(self, width, height):
        self.position = {'x': 0, 'y': 0}
        self.velocity = {'x': 1, 'y': 1}
        self.width = width
        self.height = height

    def to_dict(self):
        return {
            'position': self.position,
            'velocity': self.velocity,
            'width': self.width,
            'height': self.height
        }

    def move(self, player_1_paddle, player_2_paddle):
        # Update the ball's position based on its velocity
        self.position['x'] += self.velocity['x']
        self.position['y'] += self.velocity['y']

        # Check if the ball passed a player's paddle
        if self.position['x'] < player_1_paddle.paddle.position['x']:
            # Player 2 scores a point
            player_2_paddle.player_score += 1
            # Reset the ball position (modify based on your game's logic)
            self.position = {'x': 0, 'y': 0}
        elif self.position['x'] > player_2_paddle.paddle.position['x'] + player_2_paddle.paddle.width:
            # Player 1 scores a point
            player_1_paddle.player_score += 1
            # Reset the ball position (modify based on your game's logic)
            self.position = {'x': 0, 'y': 0}

    def collides_with_paddle(self, paddle):
        # Check for collision with the paddle
        if (
            self.position['x'] + self.width >= paddle.position['x'] and
            self.position['x'] <= paddle.position['x'] + paddle.width and
            self.position['y'] + self.height >= paddle.position['y'] and
            self.position['y'] <= paddle.position['y'] + paddle.height
        ):
            return True
        return False

    def collides_with_wall(self, wall_width, wall_height):
        # Check for collision with the walls
        if (
            self.position['x'] <= 0 or
            self.position['x'] + self.width >= wall_width or
            self.position['y'] <= 0 or
            self.position['y'] + self.height >= wall_height
        ):
            return True
        return False

class Paddle:
    def __init__(self, width=10, height=60):
        self._width = width
        self._height = height
        self._position = {'x': 0, 'y': 0}

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

    def move_up(self, distance=5):
        self._position['y'] -= distance

    def move_down(self, distance=5):
        self._position['y'] += distance

    def __str__(self):
        return f"Paddle - Width: {self.width}, Height: {self.height}, Position: {self.position}"

    # Remove the __dict__ method

class Player(object):
    def __init__(self, player_number, player_id, player_channel_name):
        self.player_number = player_number
        self.player_id = player_id
        self.player_channel_name = player_channel_name
        self._player_score = 0
        self._paddle = Paddle() 
        self._keyboard_input = {}

    def __str__(self):
        return f'Player {self.player_number}: {self.player_id}, Score: {self.player_score}, {self.paddle}'

    # Properties for getter and setter methods
    @property
    def player_score(self):
        return self._player_score

    @player_score.setter
    def player_score(self, value):
        self._player_score = value

    @property
    def paddle(self):
        return self._paddle

    @paddle.setter
    def paddle(self, value):
        self._paddle = value

    @property
    def keyboard_input(self):
        return self._keyboard_input

    @keyboard_input.setter
    def keyboard_input(self, value):
        self._keyboard_input = value

    # Methods for getting player information
    def get_player_number(self):
        return self.player_number

    def get_player_id(self):
        return self.player_id

    def get_player_channel_name(self):
        return self.player_channel_name

    # Methods for setting player information
    def set_player_number(self, player_number):
        self.player_number = player_number

    def set_player_id(self, player_id):
        self.player_id = player_id

    def set_player_channel_name(self, player_channel_name):
        self.player_channel_name = player_channel_name

    def move_paddle_up(self, distance=5):
        self.paddle.move_up(distance)

    def move_paddle_down(self, distance=5):
        self.paddle.move_down(distance)

    def to_dict(self):
        return {
            'player_number': self.player_number,
            'player_id': self.player_id,
            'player_channel_name': self.player_channel_name,
            'player_score': self.player_score,
            'paddle': self.paddle.__dict__,  # Use the default __dict__ attribute here
            'keyboard_input': self.keyboard_input
        }

class MatchConsumer(AsyncWebsocketConsumer):
    
    list_of_match_consumers = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ball = Ball(10, 10)
        self.list_of_players = []
        self.observers = []

    async def connect(self):
        self.query_params = parse_qs(self.scope['query_string'].decode())
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.player_1_id = self.query_params.get('player_1', [None])[0]
        self.player_2_id = self.query_params.get('player_2', [None])[0]
        self.client_id = self.query_params.get('client_id', [None])[0]
        self.player = None
        self.game_mode = self.query_params.get('game_mode', ['1v1'])[0]

        try:
            if self.client_id == self.player_1_id or self.client_id == self.player_2_id:
                # Accept the connection
                await self.accept()
                # Add the player to the group
                await self.channel_layer.group_add(
                    self.match_id,
                    self.channel_name
                )
                # Add the player to the list of players
                self._add_player_to_list_of_players(self.client_id, self.channel_name)

                # Send the player the command 'start_match'
                await self._send_info_to_client('match_id', f'{self.match_id}')
                # Announce the player's presence to the group
                await self.channel_layer.group_send(
                    self.match_id,
                    {
                        'type': 'send_info_to_all_players',
                        'info': f'{self.client_id} has joined the match.'
                    }
                )
            else:
                # They're observing the match
                # Accept the connection
                await self.accept()
                # Add the player to the group
                await self.channel_layer.group_add(
                    self.match_id,
                    self.channel_name
                )
                # Add the player to the list of observers
                await self._add_player_to_list_of_observers(self.client_id, self.channel_name)
                # Send the player the current state of the match
                await self._send_match_state()

        except ValueError:
            # Something went wrong
            await self.close()

    async def disconnect(self, close_code):
        # Remove the player from the list of players
        self._remove_player_from_list_of_players(self.client_id)
        # Remove the player from the list of observers
        self._remove_player_from_list_of_observers(self.client_id)
        # Remove the player from the group
        await self.channel_layer.group_discard(
            self.match_id,
            self.channel_name
        )

    def _get_user_model(self, client_id):
        from api.userauth.models import CustomUser as User
        try:
            user = User.objects.get(pk=client_id)
            return user
        except User.DoesNotExist:
            return None

    def _add_player_to_list_of_players(self, client_id, channel_name):
        # Add the player to the list of players
        
        print(f"Adding player to list of players: {client_id}")
        if client_id == self.player_1_id:
            player_1 = Player(player_number=1, player_id=client_id, player_channel_name=channel_name)
            self.list_of_players.append(player_1)
        elif client_id == self.player_2_id:
            player_2 = Player(player_number=2, player_id=client_id, player_channel_name=channel_name)
            self.list_of_players.append(player_2)
        else:
            return False

        print(f"List of players: {self.list_of_players}")
        return True

    def _remove_player_from_list_of_players(self, client_id):
        # Remove the player from the list of players
        for player in self.list_of_players:
            if player.player_id == client_id:
                self.list_of_players.remove(player)

    def _add_player_to_list_of_observers(self, client_id, channel_name):
        # Add the player to the list of observers
        self.observers.append((client_id, channel_name))
        return True
    
    def _remove_player_from_list_of_observers(self, client_id):
        # Remove the player from the list of observers
        for observer in self.observers:
            if observer[0] == client_id:
                self.observers.remove(observer)
                return True
        return False
    
    async def _send_info_to_client(self, command, info):
        # Send the player the current state of the match
        print(f"Sending info to client: {info}")
        print(f"Command: {command}")
        await self.send(text_data=json.dumps({
            'command': command,
            'info': info
        }))

    async def send_info_to_all_players(self, event):
        # Send info to all players
        await self.send(text_data=json.dumps({
            'command': 'info',
            'info': event['info']
        }))

    async def _send_match_state(self):
        # Send the player the current state of the match
        await self.send(text_data=json.dumps({
            'command': 'match_state',
            'match_state': self._get_match_state(),
        }))

    def _get_match_state(self):
        match_state = {
            'game_mode': self.game_mode
        }
        player_1 = self.list_of_players[0]
        player_2 = self.list_of_players[1]
        # Include player details
        match_state['player_1'] = player_1.to_dict()
        match_state['player_2'] = player_2.to_dict()


        # Include ball details
        match_state['ball'] = self.ball.to_dict()

        print(f"Match state: {match_state}")
        return match_state

    def _get_list_of_players(self):
        # Get the list of players
        list_of_players = []
        for player in self.list_of_players:
            list_of_players.append(player.__dict__)
        return list_of_players
    
    def _get_list_of_observers(self):
        # Get the list of observers
        list_of_observers = []
        for observer in self.observers:
            list_of_observers.append(observer)
        return list_of_observers
    
    async def _send_match_state_to_all_players(self):
        # Send the current state of the match to all players
        print(f"Sending match state to all players: {self._get_match_state()}")
        await self.channel_layer.group_send(
            self.match_id,
            {
                'type': 'send_match_state_to_all_players',
                'match_state': self._get_match_state()
            }
        )

    async def send_match_state_to_all_players(self, event):
        # Send the current state of the match to all players
        await self.send(text_data=json.dumps({
            'command': 'match_state',
            'match_state': event['match_state']
        }))

    async def receive(self, text_data):
        # Receive a message from the player
        data = json.loads(text_data)
        command = data.get('command')
        info = data.get('info')

        if command == 'start_match':
            await self._start_match()
        elif command == 'pause_match':
            await self.pause_match()
        elif command == 'end_match':
            await self.end_match()
        elif command == 'start_ball':
            await self._start_ball()
        elif command == 'stop_ball':
            await self._stop_ball() 
        elif command == 'keyboard_input':
            await self._keyboard_input(info)

        else:
            print(f"Invalid command: {command}")
            await self._send_info_to_client('error', f'Invalid command: {command}')

    async def _start_match(self):
        # Send the player the command 'start_match'
        await self._send_info_to_client('info', 'match_starting')

        # Check if there are at least two players to start the match
        print(f"List of players: {self.list_of_players}")
        if len(self.list_of_players) >= 1:
            # Initialize match state and start the game loop
            self.ball.position['x'] = 200
            self.ball.position['y'] = 200
            # ... (rest of the initialization code)

            # Inform all players about the initial state
            await self._send_match_state_to_all_players()

            print(f"Starting match: {self.match_id}")
            # Start the game loop
            await self._game_loop()

            # Notify players that the match has ended
            await self._send_info_to_client('info', 'match_ended')
        else:
            # Handle the case when there are not enough players to start the match
            await self._send_info_to_client('error', 'Not enough players to start the match.')

    async def pause_match(self):
        # Send the player the command 'pause_match'
        await self._send_info_to_client('info', 'match_paused')

        # Pause the game loop
        self.game = False

        # Notify players that the match has been paused
        await self._send_info_to_client('info', 'match_paused')

    async def end_match(self):
        # Send the player the command 'end_match'
        await self._send_info_to_client('info', 'match_ended')

        # End the game loop
        self.game = False

        # Notify players that the match has ended
        await self._send_info_to_client('info', 'match_ended')

    async def _start_ball(self):
        # Send the player the command 'start_ball'
        await self._send_info_to_client('info', 'ball_started')

        # Start the ball
        self.ball.velocity['x'] = 1
        self.ball.velocity['y'] = 1

        # Notify players that the ball has started
        await self._send_info_to_client('info', 'ball_started')

    async def _stop_ball(self):
        # Send the player the command 'stop_ball'
        await self._send_info_to_client('info', 'ball_stopped')

        # Stop the ball
        self.ball.velocity['x'] = 0
        self.ball.velocity['y'] = 0

        # Notify players that the ball has stopped
        await self._send_info_to_client('info', 'ball_stopped')

    async def _game_loop(self):
        
        while self.game:
            # Update game state, check collisions, etc.
            self.timer += 1
            if self.timer % 1000 == 0:
                self.score += 1
                self.timer = 0
            if self.score == 5:
                self.game = False

            # Update ball and paddle positions, handle collisions, etc.
            for player in self.list_of_players:
                if player.keyboard_input.get('up'):
                    player.paddle.move_up()
                if player.keyboard_input.get('down'):
                    player.paddle.move_down()

            # Check if there are at least two players before accessing elements
            if len(self.list_of_players) >= 2:
                self.ball.move(self.list_of_players[0], self.list_of_players[1])
            else:
                # Handle the case when there are not enough players
                print("Not enough players to continue the game.")

            self.ball.move(self.list_of_players[0], self.list_of_players[1])

            # Check for collisions with paddles
            for player in self.list_of_players:
                if self.ball.collides_with_paddle(player.paddle):
                    # Handle collision logic here, e.g., reverse ball's direction
                    self.ball.velocity['x'] *= -1

            # Check for collisions with walls
            if self.ball.collides_with_wall(WALL_WIDTH = 800, WALL_HEIGHT = 600):
                # Handle collision logic here, e.g., reverse ball's direction
                self.ball.velocity['x'] *= -1
                self.ball.velocity['y'] *= -1

            # Send the updated state to all players
            await self._send_match_state_to_all_players()

            # Small delay to control the game loop speed
            await asyncio.sleep(0.01)



# Example Usage:
# paddle = Paddle(width=12, height=50)
# print(paddle)  # Output: Paddle - Width: 12, Height: 50, Position: {'x': 0, 'y': 0}

# # Move the paddle
# paddle.move_down(10)
# print(paddle)  # Output: Paddle - Width: 12, Height: 50, Position: {'x': 0, 'y': 10}

# Example usage:
# player = Player(player_number=1, player_id=101, player_channel_name='channel_1')
# player.player_score = 100  # Using the property setter
# player.paddle = 'Some Paddle'  # Using the property setter
# player.keyboard_input = {'key': 'value'}  # Using the property setter

# Accessing properties
# print(player.player_score)  # Using the property getter
# print(player.paddle)  # Using the property getter
# print(player.keyboard_input)  # Using the property getter

# Example Usage:
# player = Player(player_number=1, player_id=101, player_channel_name="channel_1")
# print(player)  # Output: Player 1: 101, Score: 0, Paddle - Width: 10, Height: 60, Position: {'x': 0, 'y': 0}

# # Move the player's paddle
# player.move_paddle_down(10)
# print(player)  # Output: Player 1: 101, Score: 0, Paddle - Width: 10, Height: 60, Position: {'x': 0, 'y': 10}