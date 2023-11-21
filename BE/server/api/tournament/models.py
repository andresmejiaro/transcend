from django.db import models
from django.contrib.auth.models import User

class Tournaments(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Matches(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, null=True, blank=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jugador1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jugador2')
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Partida {self.id} - {self.jugador1} vs {self.jugador2}"
