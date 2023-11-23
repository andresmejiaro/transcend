from django.db import models
from api.userauth.models import CustomUser as User

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2')
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    # active: Whether or not the match is currently being played so others can view it.
    # If the match is not active, it is either waiting for the players to join or it is finished.
    # Users in active matches cannot receive new match requests.
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Match {self.id} - {self.player1} vs {self.player2}"

class Tournament(models.Model):
    # name: Type of tournament (e.g. 1v1, bracket, etc.)
    name = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    # matches: List of matches in within the tournament. In a 1v1 there would only be one match.
    # In a bracket tournament, there would be multiple matches.
    matches = models.ManyToManyField(Match, blank=True)

    def __str__(self):
        return f"Tournament {self.id} - {self.name}"
