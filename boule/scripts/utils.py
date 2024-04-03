from ..models import Match, Player, PlayerMatch
from ..forms import PlayerForm, MatchForm
from datetime import datetime, timedelta
import math


def run():
    players = Player.objects.prefetch_related("player_matches__match")
    scores = {}
    for player in players:

        wins = 0
        losses = 0
        points_plus = 1
        points_minus = 1
        player_matches = player.player_matches.all()

        for player_match in player_matches:

            team_1_points = player_match.match.team_1_points
            team_2_points = player_match.match.team_2_points

            if player_match.team == 1:

                points_plus += team_1_points
                points_minus += team_2_points
                if team_1_points > team_2_points:
                    wins += 1
                else:
                    losses += 1

            elif player_match.team == 2:

                points_plus += team_2_points
                points_minus += team_1_points
                if team_2_points > team_1_points:
                    wins += 1
                else:
                    losses += 1

        score = math.ceil((wins * 2 - losses) * (points_plus / points_minus))
        scores[player] = score

    final_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
