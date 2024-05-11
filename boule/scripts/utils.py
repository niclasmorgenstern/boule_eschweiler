from ..models import Match, Player, PlayerMatch
from ..forms import PlayerForm, MatchForm
from datetime import datetime, timedelta
import math
import time
from ..services import (
    calc_year_ranking,
    calc_month_ranking,
    calc_ranking,
    calc_player_stats,
)
from django.db.models import Q


def run():
    year = 2024
    month = 3
    player = Player.objects.all()
    stats = calc_month_ranking(player, month, year)

    print(stats)

    calc_year_ranking(player, year)

    # total_players = sum([len(players) for rank, players in stats.items()])
    # print(total_players)

    # for rank, players in stats.items():
    #     for player, score in players:
    #         print(player.first_name, score)
