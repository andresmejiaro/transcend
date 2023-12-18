from django.contrib import admin

# api/tournament/admin.py
from api.tournament.models.round_model import Round
from api.tournament.models.match_model import Match
from api.tournament.models.tournament_model import Tournament

admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Round)
