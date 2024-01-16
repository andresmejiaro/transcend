from django.db import models
from api.userauth.models import CustomUser as User
from api.tournament.models import Match

# Create your models here.
class BestofThree(models.Model):
    name = models.CharField(max_length=100)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BOT_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BOT_player2', null=True)
    match1 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match1', null=True)
    match2 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match2', null=True)
    match3 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match3', null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BOT_winner', blank=True, null=True)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Best of Three {self.id} - {self.player1} vs {self.player2}"