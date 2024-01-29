from pygments.lexers import data

from ..user import CustomUser

class UserUpdateValidator:
    def __init__(self, data):
        self.raw_data = data
        self.valid = True
        self.errors = {}

    def set_error(self, key, reason):
        self.valid = False
        self.errors[key] = reason

    def validate_username(self):
        username = self.raw_data.get('username')
        if not username:
            return
        if CustomUser.objects.filter(username=username).exists():
            self.set_error(key='username', reason='Duplicate username')
        if len(username) > 20:
            self.set_error(key='username', reason='Username too long')

    def validate_email(self):
        email = self.raw_data.get('email')
        if not email:
            return
        if email.endswith('student.42madrid.com'):
            self.set_error(key='email', reason='Email can not be from 42madrid.')
        elif CustomUser.objects.filter(email=email).exists():
            self.set_error(key='email', reason='Duplicate email')
        elif len(email) > 100:
            self.set_error(key='username', reason='Username too long')

    def validate_full_name(self):
        full_name = self.raw_data.get('full_name')
        if not full_name:
            return
        if len(full_name) > 50:
            self.set_error(key='full_name', reason='Name too long')

    def validate(self):
        self.validate_username()
        self.validate_email()
        self.validate_full_name()
        return self.errors
