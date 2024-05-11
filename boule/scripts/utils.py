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
    get_player_ranking,
)
from django.db.models import Q


def run():
    year = 2024
    month = 1
    player_one = Player.objects.get(id=4)
    player = Player.objects.all()
    stats = calc_year_ranking(player, year=year)
    rank, score = get_player_ranking(player_one, stats)
    print(rank, score)
