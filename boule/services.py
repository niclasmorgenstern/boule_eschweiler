import math


def calc_ranking_score(wins, losses, points_plus, points_minus):
    return math.ceil((wins * 2 - losses) * (points_plus / points_minus))


def calc_player_stats(player, month=None, year=None):
    wins = 0
    losses = 0
    points_plus = 1
    points_minus = 1
    player_matches = player.player_matches.all()

    if month is not None:
        player_matches = player_matches.filter(match__date__month=month)
    if year is not None:
        player_matches = player_matches.filter(match__date__year=year)

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

    score = calc_ranking_score(wins, losses, points_plus, points_minus)

    player_stats = {
        "games": wins + losses,
        "wins": wins,
        "losses": losses,
        "points_plus": points_plus - 1,
        "points_minus": points_minus - 1,
        "score": score,
    }

    return player_stats


def calc_ranking(players, month=None, year=None):
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
