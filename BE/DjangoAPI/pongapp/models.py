from django.db import models


# Create your models here.
class Tournament(models.Model):
    TournamentID = models.AutoField(primary_key=True)
    TournamentName = models.CharField(max_length=100)

class Player(models.Model):
    PlayerID = models.AutoField(primary_key=True)
    PlayerName = models.CharField(max_length=100)
    PlayerEmail = models.CharField(max_length=100)
    PlayerPassword = models.CharField(max_length=100)
    PlayerTournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
