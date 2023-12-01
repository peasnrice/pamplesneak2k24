from django.urls import path
from gameroom import views  # Import views from the current app

app_name = 'gameroom'

urlpatterns = [
    # path('', views.pamplesneak, name='pamplesneak'),
    path('pampleplay/', views.pampleplay, name='pampleplay'),
    path('pampleplay/create', views.creategame, name='creategame'),
]
