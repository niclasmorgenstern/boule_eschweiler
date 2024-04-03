from django import forms
from .models import Player, Match
from django.core.exceptions import ValidationError
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
            "name",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "py-2 px-4 border-2 border-gray-400 rounded",
                    "placeholder": "Name",
                }
            )
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
    from datetime import datetime

    date = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), initial=get_last_wednesday
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

    def clean(self):
        cleaned_data = super().clean()
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
