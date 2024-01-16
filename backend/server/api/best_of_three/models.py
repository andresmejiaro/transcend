from django.db import models
from api.userauth.models import CustomUser as User
from api.tournaments.models import Match


# Create your models here.
class BestofThree(models.Model):
    name = models.CharField(max_length=100)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2', null=True)
    match1 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match1', null=True)
    match2 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match2', null=True)
    match3 = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match3', null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
