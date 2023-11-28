from django.contrib import admin

# Register your models here.
from .models import Tournament, Match, Round

admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Round)
