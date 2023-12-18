from django.db import models
from api.userauth.models import CustomUser as User

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    round = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner_tournament', blank=True, null=True)
    tournament_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tournament_admin', blank=True, null=True)
    players = models.ManyToManyField(User, blank=True)
    observers = models.ManyToManyField(User, blank=True, related_name='observers')

    def __str__(self):
        return f"Tournament {self.id} - {self.name}"