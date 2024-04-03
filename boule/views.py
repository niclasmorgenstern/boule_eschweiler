from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView
from django.urls import reverse
from django.contrib import messages
import math

from .models import Player, Match, PlayerMatch
from .forms import PlayerForm, MatchForm


class RankingView(View):

    def get(self, request, *args, **kwargs):

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
        print(final_scores)

        return render(request, "ranking.html", {"scores": final_scores})


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


class MatchListView(ListView):
    model = Match
    template_name = "match/match_list.html"

    def get_queryset(self):
        queryset = Match.objects.prefetch_related("player_matches").order_by("-date")
        return queryset


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
