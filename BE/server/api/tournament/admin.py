from django.contrib import admin

# Register your models here.
from .models import Tournaments, Matches

admin.site.register(Tournaments)
admin.site.register(Matches)