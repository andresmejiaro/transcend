from django.db import models
from api.userauth.models import CustomUser as User

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2', null=True)
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def loser(self):
        return self.player1 if self.winner == self.player2 else self.player2

    def __str__(self):
        return f"Match {self.id} - {self.player1} vs {self.player2}"