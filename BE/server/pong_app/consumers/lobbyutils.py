# lobbycommands.py

class LobbyCommands(object):
    def __init__(self, lobby_consumer):
        self.lobby_consumer = lobby_consumer
        self.lobby_functions = LobbyFunctions(lobby_consumer)

    async def execute_command(self, command, data):
        # Get the method corresponding to the command
        method = getattr(self, command, None)
        if callable(method):
            # Call the method with the provided data
            await method(data)
            print(f"Executed command: {command}")
            print(f"Data: {data}")
        else:
            print(f"Invalid command: {command}")

        
    # Group CRUD
    async def create_group(self, data):
        room_name = data.get('group_name')
        await self.lobby_functions._create_a_group(room_name)

    async def delete_group(self, data):
        room_name = data.get('group_name')
        await self.lobby_functions._delete_a_group(room_name)

    async def change_group_name(self, data):
        old_room_name = data.get('old_group_name')
        new_room_name = data.get('new_group_name')
        await self.lobby_functions._change_room_name(old_room_name, new_room_name)
    # -------------------------------

    # Group User Methods
    async def remove_user_from_group(self, data):
        group_name = data.get('group_name')
        user_id = data.get('user_id')
        await self.lobby_functions._remove_user_from_group(group_name, user_id)

    async def add_user_to_group(self, data):
        group_name = data.get('group_name')
        user_id = data.get('user_id')
        await self.lobby_functions._add_user_to_group(group_name, user_id)

    async def get_group_user_count(self, data):
        group_name = data.get('group_name')
        await self.lobby_functions._send_group_member_count(group_name)

    async def get_group_user_list(self, data):
        group_name = data.get('group_name')
        await self.lobby_functions._send_group_member_list(group_name)
    # -------------------------------

    # Message commands
    async def send_message(self, data):
        group_name = data.get('group_name')
        message = data.get('message')
        sender = data.get('sender')
        print(f"{sender}: Sending message: {message} to group: {group_name}")
        await self.lobby_functions._send_message(group_name, message) 

    async def send_private_message(self, data):
        recipient = data.get('recipient')
        message = data.get('message')
        sender = data.get('sender')
        print(f"{sender}: Sending message: {message} to recipient: {recipient}")
        await self.lobby_functions._send_private_message(recipient, message)
    # -------------------------------

    # Challenge commands
    async def send_challenge(self, data):
        group_name = data.get('group_name')
        await self.lobby_functions._send_challenge(group_name)

    async def accept_challenge(self, data):
        group_name = data.get('group_name')
        await self.lobby_functions._accept_challenge(group_name)

    async def decline_challenge(self, data):
        group_name = data.get('group_name') 
        await self.lobby_functions._decline_challenge(group_name)
    # -------------------------------

    # User commands
    async def get_user_list(self, data):
        await self.lobby_functions._send_user_list()

    async def get_website_user_list(self, data):
        await self.lobby_functions._send_website_user_list()
    # -------------------------------


# lobbyfunctions.py
class LobbyFunctions(object):
    def __init__(self, lobby_consumer):
        self.lobby_consumer = lobby_consumer

    async def _create_a_group(self, room_name):
        await self.lobby_consumer.channel_layer.group_add(
            room_name,
            self.lobby_consumer.channel_name
        )
        self.lobby_consumer.create_a_group(room_name)
        await self.lobby_consumer.send_group_list()

        
        