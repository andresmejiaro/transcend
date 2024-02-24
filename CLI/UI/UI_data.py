import logging

from utils.logger import log_message

class UIData:
    def __init__(self):
        # Define your data attributes here with default values
        self.pending_invitations = []
        self.sent_invitations = []
        self.friends_list = []
        self.online_users = []

    @property
    def pending_invitations_count(self):
        return len(self.pending_invitations)
    
    @property
    def sent_invitations_count(self):
        return len(self.sent_invitations)
    
    @property
    def friends_list_count(self):
        return len(self.friends_list)
    
    @property
    def online_users_count(self):
        return len(self.online_users)
    
    def add_item(self, category, item):
        getattr(self, category).append(item)

    def remove_item(self, category, item):
        getattr(self, category).remove(item)

    def clear_items(self, category):
        getattr(self, category).clear()

    def clear_all_data(self):
        self.clear_items('pending_invitations')
        self.clear_items('sent_invitations')
        self.clear_items('friends_list')
        self.clear_items('online_users')

    def print_data(self):
        log_message(f"Pending Invitations: {self.pending_invitations}", level=logging.DEBUG)
        log_message(f"Sent Invitations: {self.sent_invitations}", level=logging.DEBUG)
        log_message(f"Friends List: {self.friends_list}", level=logging.DEBUG)
        log_message(f"Online Users: {self.online_users}", level=logging.DEBUG)

    def print_data_counts(self):
        log_message(f"Pending Invitations Count: {self.pending_invitations_count}", level=logging.DEBUG)
        log_message(f"Sent Invitations Count: {self.sent_invitations_count}", level=logging.DEBUG)
        log_message(f"Friends List Count: {self.friends_list_count}", level=logging.DEBUG)
        log_message(f"Online Users Count: {self.online_users_count}", level=logging.DEBUG)

    def print_data_counts_and_data(self):
        self.print_data_counts()
        self.print_data()

    @property
    def all_counts(self):
        return {
            'pending_invitations': self.pending_invitations_count,
            'sent_invitations': self.sent_invitations_count,
            'friends_list': self.friends_list_count,
            'online_users': self.online_users_count,
        }

    def is_online(self, username):
        return username in self.online_users

    def get_friends_list(self):
        return self.friends_list.copy()
