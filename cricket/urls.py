from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("teams", views.teams, name="teams"),
    path("game", views.game, name="game"),
    path("gamecontent", views.gamecontent, name="gamecontent"),
    path("state", views.state, name="state"),
    path("next_batsman", views.next_batsman, name="next_batsman"),
    path("next_bowler", views.next_bowler, name="next_bowler"),
    path("empty_spots", views.empty_spots, name="empty_spots"),
    path("winner", views.winner, name="winner")
]