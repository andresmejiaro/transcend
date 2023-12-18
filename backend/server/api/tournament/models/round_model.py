from django.db import models
from .tournament_model import Tournament
from .match_model import Match

class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(verbose_name='Round Number', default=0)
    matches = models.ManyToManyField(Match, blank=True)

    def __str__(self):
        return f"Round {self.round_number} of {self.tournament}"