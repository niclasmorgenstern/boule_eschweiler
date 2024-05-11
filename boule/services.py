import math
import time
from collections import defaultdict


def calc_ranking_score(wins, losses, points_plus, points_minus):
    return math.ceil((wins * 2 - losses) * min((points_plus / points_minus), 2))


def calc_win_bonus(loser_score):
    if loser_score == 0:
        return 0.5
    elif loser_score == 1:
        return 0.25
    elif loser_score == 2:
        return 0.1
    else:
        return 0


def calc_loss_bonus(loser_score):
    if loser_score == 12:
        return 0.5
    elif loser_score == 11:
        return 0.25
    elif loser_score == 10:
        return 0.1
    else:
        return 0


def calc_player_stats(player, month=None, year=None):

    wins = 0
    losses = 0
    points_plus = 1
    points_minus = 1
    bonus_points = 0
    player_matches = player.player_matches.select_related("match")

    if month != "" and month is not None:
        player_matches = player_matches.filter(match__date__month=month)
    if year != "" and year is not None:
        player_matches = player_matches.filter(match__date__year=year)

    if not player_matches:
        return None

    for player_match in player_matches:

        team_1_points = player_match.match.team_1_points
        team_2_points = player_match.match.team_2_points

        if player_match.team == 1:

            points_plus += team_1_points
            points_minus += team_2_points

            if team_1_points > team_2_points:
                wins += 1
                bonus_points += calc_win_bonus(team_2_points)
            else:
                losses += 1
                bonus_points += calc_loss_bonus(team_1_points)

        elif player_match.team == 2:

            points_plus += team_2_points
            points_minus += team_1_points

            if team_2_points > team_1_points:
                wins += 1
                bonus_points += calc_win_bonus(team_1_points)
            else:
                losses += 1
                bonus_points += calc_loss_bonus(team_2_points)

    score = calc_ranking_score(wins, losses, points_plus, points_minus) + bonus_points

    player_stats = {
        "games": wins + losses,
        "wins": wins,
        "losses": losses,
        "points_plus": points_plus - 1,
        "points_minus": points_minus - 1,
        "score": score,
    }

    return player_stats


def calc_ranking(scores):

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranking = defaultdict(list)
    rank = 0
    prev_score = None
    skip_ranks = 1
    for player, score in sorted_scores:
        if score != prev_score:
            rank += skip_ranks
            skip_ranks = 1
        else:
            skip_ranks += 1
        ranking[rank].append((player, score))
        prev_score = score

    return dict(ranking)


def calc_month_ranking(players, month=None, year=None):

    scores_month = {}

    for player in players:
        player_stats = calc_player_stats(player, month=month, year=year)
        if player_stats:
            scores_month[player] = player_stats["score"]

    ranking_month = calc_ranking(scores_month)

    return ranking_month


def calc_year_ranking(players, year=None):

    scores_year = defaultdict(int)

    for month in range(12):
        ranking_month = calc_month_ranking(players, month=month, year=year)
        if ranking_month:
            month_max_points = sum([len(players) for players in ranking_month.values()])
            for rank, info in ranking_month.items():
                for player, score in info:

                    match rank:
                        case 1:
                            rank_bonus_points = 3
                        case 2:
                            rank_bonus_points = 2
                        case 3:
                            rank_bonus_points = 1
                        case _:
                            rank_bonus_points = 0

                    scores_year[player] += (
                        month_max_points + 1 - rank + rank_bonus_points
                    )

    ranking_year = calc_ranking(scores_year)
    return ranking_year


def calc_year_ranking_v2(players, month=None, year=None):
    scores = {}

    for player in players:
        player_stats = calc_player_stats(player, month=month, year=year)
        scores[player] = player_stats["score"]

    final_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranking = {
        rank: {"player": player, "score": score}
        for rank, (player, score) in enumerate(final_scores, 1)
    }

    return ranking


months = {
    "1": "Januar",
    "2": "Februar",
    "3": "März",
    "4": "April",
    "5": "Mai",
    "6": "Juni",
    "7": "Juli",
    "8": "August",
    "9": "September",
    "10": "Oktober",
    "11": "November",
    "12": "Dezember",
}
