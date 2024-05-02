from django import forms
from .models import Player, Match
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from datetime import datetime, timedelta


def get_last_wednesday():
    current_date = datetime.now().date()
    today = current_date.weekday()
    days_to_subtract = (today - 2) % 7
    last_wednesday = current_date - timedelta(days=days_to_subtract)
    return last_wednesday


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = [
            "first_name",
            "last_name",
        ]
        labels = {
            "first_name": "Vorname",
            "last_name": "Nachname",
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "Ein Spieler mit diesem Namen existiert bereits.",
            }
        }


class MatchForm(forms.ModelForm):

    team_1_player_1 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
    )
    team_1_player_2 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
        required=False,
    )
    team_1_player_3 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
        required=False,
    )
    team_2_player_1 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
    )
    team_2_player_2 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
        required=False,
    )
    team_2_player_3 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        empty_label="---------",
        label="Spieler",
        required=False,
    )

    date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}),
        initial=get_last_wednesday,
        label="Datum",
    )

    class Meta:
        model = Match
        fields = [
            "date",
            "team_1_points",
            "team_2_points",
        ]
        labels = {
            "date": "Datum",
            "team_1_points": "Team 1",
            "team_2_points": "Team 2",
        }
        widgets = {
            "team_1_points": forms.Select(choices=[(i, str(i)) for i in range(14)]),
            "team_2_points": forms.Select(choices=[(i, str(i)) for i in range(14)]),
        }

    def _validate_unique_players(self, cleaned_data):

        players = [
            player
            for player in [
                cleaned_data["team_1_player_1"],
                cleaned_data["team_1_player_2"],
                cleaned_data["team_1_player_3"],
                cleaned_data["team_2_player_1"],
                cleaned_data["team_2_player_2"],
                cleaned_data["team_2_player_3"],
            ]
            if player is not None
        ]
        if len(players) != len(set(players)):
            raise ValidationError("Jeder Spieler darf nur einmal ausgewählt werden.")

    def _validate_score(self, cleaned_date):

        team_1_points = cleaned_date["team_1_points"]
        team_2_points = cleaned_date["team_2_points"]

        if team_1_points != 13 and team_2_points != 13:
            raise ValidationError(
                "Eins der Teams sollte der Gewinner mit 13 Punkten sein."
            )

        if team_1_points == team_2_points:
            raise ValidationError("Beide Teams können nicht die selben Punkte haben.")

    def clean(self):

        cleaned_data = super().clean()
        self._validate_unique_players(cleaned_data)
        self._validate_score(cleaned_data)
