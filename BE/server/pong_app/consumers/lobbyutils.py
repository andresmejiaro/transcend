# lobbycommands.py

class LobbyCommands(object):
    def __init__(self, lobby_consumer):
        self.lobby_consumer = lobby_consumer
        self.lobby_functions = LobbyFunctions(lobby_consumer)

    # Execute the command
    async def execute_command(self, command, data):
        # Get the method corresponding to the command
        method = getattr(self, command, None)
        if callable(method):
            # Call the method with the provided data
            print(f"Executing command: {command}")
            await method(data)
            print(f"Executed command: {command}")
            
        else:
            print(f"Invalid command: {command}")
            await self.lobby_consumer.send_info_to_client('error', f'Invalid command: {command}')

    # Global User and Group Commands
    async def get_website_user_list(self, data):
        await self.lobby_functions._send_website_user_list()
    
    async def get_website_group_list(self, data):
        await self.lobby_functions._send_website_group_list()
    # -------------------------------
    
    # Group Commands
    # Working
    async def create_group(self, data):
        print(f'Creating group: {data}')
        room_name = data.get('group_name')
        await self.lobby_functions._create_a_group(room_name)
    # Working
    async def delete_group(self, data):
        room_name = data.get('group_name')
        await self.lobby_functions._delete_a_group(room_name)
    # Working
    async def change_group_name(self, data):
        old_room_name = data.get('old_group_name')
        new_room_name = data.get('new_group_name')
        await self.lobby_functions._change_room_name(old_room_name, new_room_name)  
    # Working
    async def join_group(self, data):
        room_name = data.get('group_name')
        await self.lobby_functions._join_a_group(room_name)
    # Not Working
    async def leave_group(self, data):
        room_name = data.get('group_name')
        await self.lobby_functions._leave_a_group(room_name)
    
    # -------------------------------

    # User Commands
    # Not Working
    async def create_a_user(self, data):
        print(f'Creating user: {data}')
        client_id = data.get('client_id')
        channel_name = data.get('channel_name')
        await self.lobby_functions._create_a_user(client_id, channel_name)

# lobbyfunctions.py
class LobbyFunctions(object):
    def __init__(self, lobby_consumer):
        self.lobby_consumer = lobby_consumer

    # Global User and Group Methods
    # Working
    async def _send_website_user_list(self):
        list_of_users = self.lobby_consumer.list_of_users
        user_list = []
        for user in list_of_users:
            user_list.append(user)
        await self.lobby_consumer.send_info_to_client('information', user_list)
    # Working
    async def _send_website_group_list(self):
        list_of_groups = self.lobby_consumer.list_of_groups
        group_list = []
        for group in list_of_groups:
            group_list.append(group)
        await self.lobby_consumer.send_info_to_client('information', group_list)
    # -------------------------------

    # Group Methods
    # Working
    async def _create_a_group(self, room_name):
        print(f'Function: Creating group: {room_name}')
        if room_name in self.lobby_consumer.list_of_groups:
            await self.lobby_consumer.send_info_to_client('error', 'Group already exists')
        else:
            await self.lobby_consumer.create_a_group(room_name)
    # Working
    async def _delete_a_group(self, room_name):
        print(f'Function: Deleting group: {room_name}')
        if room_name in self.lobby_consumer.list_of_groups:
            await self.lobby_consumer.delete_a_group(room_name)
        else:
            await self.lobby_consumer.send_info_to_client('error', 'Group does not exist')
    # Working
    async def _change_room_name(self, old_room_name, new_room_name):
        print(f'Function: Changing room name from: {old_room_name} to: {new_room_name}')
        if old_room_name in self.lobby_consumer.list_of_groups:
            if new_room_name in self.lobby_consumer.list_of_groups:
                await self.lobby_consumer.send_info_to_client('error', 'Group already exists')
            else:
                await self.lobby_consumer.change_group_name(old_room_name, new_room_name)
    # Working
    async def _join_a_group(self, room_name):
        print(f'Function: Joining group: {room_name}')
        if room_name in self.lobby_consumer.list_of_groups:
            group = self.lobby_consumer.list_of_groups[room_name]
            if group.is_user_in_group(self.lobby_consumer.user):
                await self.lobby_consumer.send_info_to_client('error', 'User already in group')
            else:
                group.add_member(self.lobby_consumer.user, self.lobby_consumer.channel_name)
                self.lobby_consumer.user.add_group(group)
                await self.lobby_consumer.send_info_to_client(f'joined {room_name}', group.get_group_info())
        else:
            await self.lobby_consumer.send_info_to_client('error', 'Group does not exist')
    # Not Working
    async def _leave_a_group(self, room_name):
        print(f'Function: Leaving group: {room_name}')
        if room_name in self.lobby_consumer.list_of_groups:
            group = self.lobby_consumer.list_of_groups[room_name]
            if group.is_user_in_group(self.lobby_consumer.client_id):
                await group.remove_member(self.lobby_consumer.client_id, self.lobby_consumer.channel_name)
                self.lobby_consumer.user.remove_group(group)
                await self.lobby_consumer.send_info_to_client(f'left {room_name}', group.get_group_info())
            else:
                await self.lobby_consumer.send_info_to_client('error', 'User not in group')
        else:
            await self.lobby_consumer.send_info_to_client('error', 'Group does not exist')
    
    # -------------------------------

    # User Methods
    # Working
    async def _create_a_user(self, client_id, channel_name):
        print(f'Function: Creating user: {client_id}')
        if client_id in self.lobby_consumer.list_of_users:
            await self.lobby_consumer.send_info_to_client('error', 'User already exists')
        else:
            await self.lobby_consumer.create_a_user(client_id, channel_name)