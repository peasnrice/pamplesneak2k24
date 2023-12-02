from django.urls import path
from gameroom import views   # Import views from the current app


app_name = 'gameroom'

urlpatterns = [
    # path('', views.pamplesneak, name='pamplesneak'),
    path('pampleplay/', views.pampleplay, name='pampleplay'),
    path('pampleplay/create', views.creategame, name='creategame'),
    path('pampleplay/<int:game_id>/<slug:slug>/', views.joingame, name='joingame'),
    path('sendword/<int:game_id>/', views.send_word, name='send_word'),
    path('ajax/refresh_word/<int:game_id>/<int:player_id>/', views.refresh_word, name='refresh_word'),
    path('ajax/word_success/<int:word_id>/<int:game_id>/<int:player_id>/', views.word_success, name='word_success'),
    path('ajax/word_fail/<int:word_id>/<int:game_id>/<int:player_id>/', views.word_fail, name='word_fail'),
]
