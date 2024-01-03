from django.contrib import admin

# Register your models here.
from .models import CustomUser, Friendship

admin.site.register(CustomUser)
admin.site.register(Friendship)
