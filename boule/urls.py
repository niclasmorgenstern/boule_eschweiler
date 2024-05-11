from django.urls import path
from .views import (
    RankingView,
    RankingMonthView,
    RankingYearView,
    PlayerListView,
    PlayerCreateView,
    PlayerEditView,
    PlayerDeleteView,
    PlayerStatView,
    StatisticsMonthView,
    StatisticsYearView,
    MatchListView,
    MatchCreateView,
    MatchEditView,
    MatchDeleteView,
)

urlpatterns = [
    path("", RankingMonthView.as_view(), name="ranking"),
    path("month/", RankingMonthView.as_view(), name="ranking-month"),
    path("year/", RankingYearView.as_view(), name="ranking-year"),
    path("player/", PlayerListView.as_view(), name="player-list"),
    path("player/add/", PlayerCreateView.as_view(), name="player-add"),
    path("player/<int:pk>/edit/", PlayerEditView.as_view(), name="player-edit"),
    path("player/<int:pk>/delete/", PlayerDeleteView.as_view(), name="player-delete"),
    path("player/<int:pk>/stats/", PlayerStatView.as_view(), name="player-stats"),
    path(
        "player/<int:pk>/statistics/month/",
        StatisticsMonthView.as_view(),
        name="player-stats-month",
    ),
    path(
        "player/<int:pk>/statistics/year/",
        StatisticsYearView.as_view(),
        name="player-stats-year",
    ),
    path("match/", MatchListView.as_view(), name="match-list"),
    path("match/add/", MatchCreateView.as_view(), name="match-add"),
    path("match/<int:pk>/edit/", MatchEditView.as_view(), name="match-edit"),
    path("match/<int:pk>/delete/", MatchDeleteView.as_view(), name="match-delete"),
]
