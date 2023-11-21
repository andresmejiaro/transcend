from django.db import models
from django.contrib.auth.models import User

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2')
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Match {self.id} - {self.player1} vs {self.player2}"


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    matches = models.ManyToManyField(Match, blank=True)

    def __str__(self):
        return f"Tournament {self.id} - {self.name}"