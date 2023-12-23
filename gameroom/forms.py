# forms.py
from django import forms
from gameroom.models import Game

class GameRoomForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['game_name']

class MessageSender(forms.Form):
    word = forms.CharField(max_length=64)
    send_anonymously = forms.BooleanField(required=False)

    def __init__(self, players, *args, **kwargs):
        super(MessageSender, self).__init__(*args, **kwargs)
        self.fields['target'] = forms.ChoiceField(choices=[(id, name) for id, name in players.items()])
        self.order_fields(['word', 'players', 'send_anonymously'])