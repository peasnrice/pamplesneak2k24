from django.urls import path
from gameroom import views  # Import views from the current app


app_name = "gameroom"

urlpatterns = [
    # path("", views.pamplesneak, name="pamplesneak"),
    path("start/", views.joingame2, name="joingame2"),
    path("pampleplay/", views.pampleplay, name="pampleplay"),
    # path("pampleplay/create", views.creategame, name="creategame"),
    # path("pampleplay/join", views.joingame2, name="joingame2"),
    path("pampleplay/<int:game_id>/<slug:slug>/stats", views.stats, name="stats"),
    path("pampleplay/<int:game_id>/<slug:slug>/", views.joingame, name="joingame"),
    path("pampleplay/<int:game_id>/<slug:slug>/lobby", views.game_lobby, name="lobby"),
    path("sendword/<int:game_id>/", views.send_word, name="send_word"),
    path("ajax/inspiration/", views.get_inspiration, name="get_inspiration"),
    path(
        "ajax/refresh_word/<int:game_id>/<int:player_id>/",
        views.refresh_word,
        name="refresh_word",
    ),
    path(
        "ajax/word_success/<int:word_id>/<int:game_id>/<int:player_id>/",
        views.word_success,
        name="word_success",
    ),
    path(
        "ajax/word_fail/<int:word_id>/<int:game_id>/<int:player_id>/",
        views.word_fail,
        name="word_fail",
    ),
    path(
        "ajax/validate_sneak/<int:game_id>/",
        views.validate_sneak,
        name="validate_sneak",
    ),
    path("ajax/reject_sneak/<int:game_id>/", views.reject_sneak, name="reject_sneak"),
    path("qr-code/<int:game_id>/<slug:slug>/", views.qr_code_view, name="qr_code"),
]
