from django.db import models
from api.userauth.models import CustomUser as User
from django.utils import timezone

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
    joinable = models.BooleanField(default=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return f"Tournament {self.id} - {self.name}"

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2', null=True)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    # best_of_three_id = models.IntegerField(blank=True, null=True)

    def loser(self):
        return self.player1 if self.winner == self.player2 else self.player2

    def __str__(self):
        return f"Match {self.id} - {self.player1} vs {self.player2}"

class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(verbose_name='Round Number', default=0)
    matches = models.ManyToManyField(Match, blank=True)

    def __str__(self):
        return f"Round {self.round_number} of {self.tournament}"
