from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView
from django.urls import reverse
from django.contrib import messages
import math
from collections import defaultdict
from datetime import datetime

from .models import Player, Match, PlayerMatch
from .forms import PlayerForm, MatchForm
from .services import calc_ranking, months


class RankingView(View):

    def get(self, request, *args, **kwargs):

        month = request.GET.get("month")
        year = request.GET.get("year")

        players = Player.objects.prefetch_related("player_matches__match")

        if month != "" and month is not None:
            players = players.filter(player_matches__match__date__month=month)
        if year != "" and year is not None:
            players = players.filter(player_matches__match__date__year=year)

        ranking = calc_ranking(players, month=month, year=year)

        current_year = datetime.now().year
        years = reversed(range(current_year - 4, current_year + 1))

        return render(
            request,
            "ranking.html",
            {
                "ranking": ranking,
                "months": months,
                "years": years,
                "selected_month": months.get(month),
                "selected_year": year,
            },
        )


class PlayerListView(ListView):

    model = Player
    template_name = "player/player_list.html"
    ordering = ["name"]


class PlayerCreateView(View):

    form_class = PlayerForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, "player/player_add.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                self.request, f"{form.cleaned_data['name']} wurde hinzugefügt!"
            )
            return HttpResponseRedirect(self.request.path_info)

        return render(request, "player/player_add.html", {"form": form})


class PlayerEditView(View):

    form_class = PlayerForm

    def get(self, request, *args, **kwargs):
        player = Player.objects.get(pk=self.kwargs["pk"])
        form = self.form_class(instance=player)
        return render(
            request, "player/player_edit.html", {"form": form, "player": player}
        )

    def post(self, request, *args, **kwargs):

        player = Player.objects.get(pk=self.kwargs["pk"])
        form = self.form_class(request.POST, instance=player)

        if form.is_valid():
            form.save()
            messages.success(
                self.request, f"{form.cleaned_data['name']} wurde editiert!"
            )
            return HttpResponseRedirect(self.request.path_info)

        return render(
            request, "player/player_edit.html", {"form": form, "player": player}
        )


class PlayerDeleteView(View):

    def get(self, request, *args, **kwargs):
        player = Player.objects.get(pk=self.kwargs["pk"])
        return render(request, "player/player_delete.html", {"player": player})

    def post(self, request, *args, **kwargs):

        player = Player.objects.get(pk=self.kwargs["pk"])
        player.delete()

        return HttpResponseRedirect(reverse("player-list"))


class PlayerStatView(View):

    def get(self, request, *args, **kwargs):
        player = Player.objects.prefetch_related("player_matches__match").get(
            pk=self.kwargs["pk"]
        )

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

        player_stats = {
            "games": wins + losses,
            "wins": wins,
            "losses": losses,
            "points_plus": points_plus - 1,
            "points_minus": points_minus - 1,
            "score": score,
        }

        return render(
            request,
            "player/player_stats.html",
            {"player": player, "player_stats": player_stats},
        )


class MatchListView(View):

    def get(self, request, *args, **kwargs):

        player = request.GET.get("player")
        month = request.GET.get("month")
        year = request.GET.get("year")

        players = Player.objects.all()
        matches = Match.objects.prefetch_related("player_matches__player").order_by(
            "-date"
        )

        if month != "" and month is not None:
            matches = matches.filter(date__month=month)
        if year != "" and year is not None:
            matches = matches.filter(date__year=year)
        if player != "" and player is not None:
            matches = matches.filter(player_matches__player__name__iexact=player)

        matches_by_date = defaultdict(list)
        for match in matches:
            matches_by_date[match.date].append(match)

        current_year = datetime.now().year
        years = reversed(range(current_year - 4, current_year + 1))

        return render(
            request,
            "match/match_list.html",
            {
                "matches_by_date": dict(matches_by_date),
                "players": players,
                "months": months,
                "years": years,
                "selected_player": player,
                "selected_month": months.get(month),
                "selected_year": year,
            },
        )


class MatchCreateView(View):

    form_class = MatchForm

    def get(self, request, *args, **kwargs):
        format = self.request.GET.get("format", "1v1")
        form = self.form_class()
        return render(request, "match/match_add.html", {"form": form, "format": format})

    def post(self, request, *args, **kwargs):
        format = self.request.GET.get("format", "1v1")
        form = self.form_class(request.POST)

        if form.is_valid():
            match = form.save()
            players_team1 = [
                player
                for player in [
                    form.cleaned_data["team_1_player_1"],
                    form.cleaned_data["team_1_player_2"],
                    form.cleaned_data["team_1_player_3"],
                ]
                if player is not None
            ]
            players_team2 = [
                player
                for player in [
                    form.cleaned_data["team_2_player_1"],
                    form.cleaned_data["team_2_player_2"],
                    form.cleaned_data["team_2_player_3"],
                ]
                if player is not None
            ]
            for player_team1 in players_team1:
                PlayerMatch.objects.create(player=player_team1, match=match, team=1)
            for player_team2 in players_team2:
                PlayerMatch.objects.create(player=player_team2, match=match, team=2)
            messages.success(self.request, "Partie wurde hinzugefügt!")
            return HttpResponseRedirect(self.request.path_info + f"?format={format}")

        return render(request, "match/match_add.html", {"form": form, "format": format})


class MatchEditView(View):

    form_class = MatchForm

    def get(self, request, *args, **kwargs):
        match = Match.objects.prefetch_related("player_matches").get(
            pk=self.kwargs["pk"]
        )
        initial_data = {}
        team_1 = []
        team_2 = []
        for playermatch in match.player_matches.all():
            if playermatch.team == 1:
                team_1.append(playermatch.player)
            elif playermatch.team == 2:
                team_2.append(playermatch.player)

        for i, player in enumerate(team_1):
            initial_data[f"team_1_player_{i+1}"] = player

        for i, player in enumerate(team_2):
            initial_data[f"team_2_player_{i+1}"] = player

        form = MatchForm(instance=match, initial=initial_data)

        return render(request, "match/match_edit.html", {"form": form, "match": match})

    def post(self, request, *args, **kwargs):

        match = Match.objects.prefetch_related("player_matches").get(
            pk=self.kwargs["pk"]
        )
        form = self.form_class(request.POST, instance=match)

        if form.is_valid():
            form.save()
            players_team1 = [
                player
                for player in [
                    form.cleaned_data["team_1_player_1"],
                    form.cleaned_data["team_1_player_2"],
                    form.cleaned_data["team_1_player_3"],
                ]
                if player is not None
            ]
            players_team2 = [
                player
                for player in [
                    form.cleaned_data["team_2_player_1"],
                    form.cleaned_data["team_2_player_2"],
                    form.cleaned_data["team_2_player_3"],
                ]
                if player is not None
            ]
            match.players.clear()
            for player_team1 in players_team1:
                PlayerMatch.objects.create(player=player_team1, match=match, team=1)
            for player_team2 in players_team2:
                PlayerMatch.objects.create(player=player_team2, match=match, team=2)
            messages.success(self.request, "Partie wurde editiert!")
            return HttpResponseRedirect(self.request.path_info)

        return render(request, "match/match_edit.html", {"form": form})


class MatchDeleteView(View):

    def get(self, request, *args, **kwargs):
        match = Match.objects.get(pk=self.kwargs["pk"])
        return render(request, "match/match_delete.html", {"match": match})

    def post(self, request, *args, **kwargs):

        match = Match.objects.get(pk=self.kwargs["pk"])
        match.delete()

        return HttpResponseRedirect(reverse("match-list"))
