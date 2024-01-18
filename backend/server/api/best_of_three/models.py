# Views for best of three

import datetime 

from django.utils import timezone
from django.db import models
from api.userauth.models import CustomUser as User
from api.tournament.models import Match

# Create your models here.
class BestofThree(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BoT_player1')
    list_of_players = models.ManyToManyField(User, blank=True, related_name='BoT_player2')
    matchs = models.ManyToManyField(Match, blank=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BoT_winner', blank=True, null=True)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Best of Three {self.id} - {self.player1} vs {self.player2}"
    
    def loser(self):
        return self.player1 if self.winner == self.player2 else self.player2
    
    def is_admin(self, user):
        return self.admin == user
    
    def is_player(self, user):
        return user in self.list_of_players.all()
    
    def is_winner(self, user):
        return self.winner == user
    
    def is_loser(self, user):
        return self.loser() == user
    
    def is_active(self):
        return self.active
    
    def is_finished(self):
        return self.winner != None
    
    def is_draw(self):
        return self.winner == None
    
    def add_player(self, user):
        if not self.is_player(user):
            self.list_of_players.add(user)
            
    def remove_player(self, user):
        if self.is_player(user):
            self.list_of_players.remove(user)
            
    def set_winner(self, user):
        if self.is_player(user):
            self.winner = user
            self.active = False
            self.date_played = timezone.now()
            self.save()
            return True
        return False