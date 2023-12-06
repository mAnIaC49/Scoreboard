from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(null=True, blank=True, upload_to="images/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class Players(models.Model):
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    type = models.CharField(max_length=2)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    matches = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    highest_wicket = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    bowls = models.IntegerField(default=0)
    given_runs = models.IntegerField(default=0)


class Game(models.Model):
    teams = models.ManyToManyField(Team, blank=True, related_name="games")
    time = models.DateTimeField(auto_now_add=True)
    end_status = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game_type = models.CharField(max_length=5, null=True)
    inning = models.IntegerField(default=1)
    over = models.IntegerField(default=0)

    # Ensure only two teams canexist in one game
    def is_valid_game(self):
        return self.teams.count() == 2
        

class Bowls(models.Model):
    BOWL_TYPES = [
        ('valid', 'Valid'),
        ('wide', 'Wide'),
        ('noball', 'No ball')
    ]

    BAT_TYPES = [
        ('6', 'Six'),
        ('4', 'Four'),
        ('1', 'One'),
        ('2', 'Two'),
        ('3', 'Three'),
        ('.', 'Dot'),
        ('out', 'Out')
    ]

    batsman = models.ForeignKey('Playing',on_delete=models.CASCADE, related_name="bowls_faced")
    bowler = models.ForeignKey('Playing',on_delete=models.CASCADE, related_name="bowls_bowled")
    bowl_type = models.CharField(max_length=10, choices=BOWL_TYPES, default="valid")
    bat_type = models.CharField(max_length=10, choices=BAT_TYPES, default='.')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="bowls")
    inning = models.IntegerField(default=1)
    over = models.IntegerField(default=1)

class Playing(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='playing')
    first = models.CharField(max_length=64, null=True)
    last = models.CharField(max_length=64, null=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player')
    bat_status = models.BooleanField(default=False)
    on_strike = models.BooleanField(default=False)
    out = models.BooleanField(default=False)
    current_bowling = models.BooleanField(default=False)
    runs = models.IntegerField(default=0)
    bowls = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    runs_given = models.IntegerField(default=0)

class TeamsPlaying(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="teamsplaying")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    batting_status = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    wickets_down = models.IntegerField(default=0)