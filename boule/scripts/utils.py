from ..models import Match, Player, PlayerMatch
from ..forms import PlayerForm, MatchForm
from datetime import datetime, timedelta
import math
from ..services import calc_year_ranking, calc_month_ranking, calc_ranking
from django.db.models import Q



def run():
    year = 2024
    players = Player.objects.prefetch_related("player_matches__match")
    players = players.filter(
        Q(player_matches__match__date__year=year)
    )
    ranking = calc_year_ranking(players, year=year)
    print(ranking)
    # calc_year_ranking(players, year=2024)