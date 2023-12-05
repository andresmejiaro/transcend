from typing import Any
from django import forms
from .models import Tournament, Match, Round
from api.userauth.models import CustomUser as User

class TournamentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TournamentForm, self).__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['round'].required = False

    class Meta:
        model = Tournament
        fields = [
            'name',
            'type',
            'start_date', 
            'end_date',
            'round',
            'players',
            'observers'
            ]
        