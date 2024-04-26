from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Match(models.Model):

    date = models.DateField()
    team_1_points = models.PositiveSmallIntegerField(default=0)
    team_2_points = models.PositiveSmallIntegerField(default=0)

    players = models.ManyToManyField(Player, through="PlayerMatch")

    def __str__(self):
        return f"{self.team_1_points} - {self.team_2_points}, ({self.date})"

    def get_winner(self):
        if self.team_1_points > self.team_2_points:
            return "team1"


class PlayerMatch(models.Model):

    class TeamChoices(models.IntegerChoices):
        TEAM_1 = 1, "Team 1"
        TEAM_2 = 2, "Team 2"

    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="player_matches"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="player_matches"
    )
    team = models.IntegerField(choices=TeamChoices)

    def __str__(self):
        return f"{self.player} - Team {self.team}"

    class Meta:
        unique_together = ["match", "player"]
