# forms.py
from django import forms
from gameroom.models import Game


class JoinGameForm(forms.Form):
    game_room_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "shadow appearance-none border rounded w-full py-2 px-3 text-black leading-tight focus:outline-none focus:shadow-outline",
                "placeholder": "Game Code",
                "maxlength": "6",
            }
        ),
    )

    def clean_field(self):
        data = self.cleaned_data["game_room_code"]
        return data.upper()


class CreateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["game_name"]
        widgets = {
            "game_name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Game Name",
                    "maxlength": "6",
                }
            ),
        }


from django import forms


class MessageSender(forms.Form):
    word = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                "class": "form-input block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            }
        ),
        label="Word / Phrase",
    )
    target = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-select block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            }
        )
    )
    send_anonymously = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(), required=False
    )

    def __init__(self, players, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].choices = [(id, name) for id, name in players.items()]
        self.order_fields(["word", "target", "send_anonymously"])
