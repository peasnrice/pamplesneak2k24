# forms.py
from django import forms
from gameroom.models import Game, Round


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

    def clean_game_room_code(self):
        data = self.cleaned_data["game_room_code"]
        return data.upper()


class CreateGameForm(forms.ModelForm):
    NUMBER_OF_ROUNDS_CHOICES = [(i, str(i)) for i in range(1, 7)] + [
        ("open", "Open Ended Game")
    ]
    ROUND_DURATION_CHOICES = [
        (5, "5 minutes"),
        (10, "10 minutes"),
        (15, "15 minutes"),
        (30, "30 minutes"),
        (45, "45 minutes"),
        (60, "60 minutes"),
    ]

    SNEAK_CREATION_DURATION_CHOICES = [
        (5, "5 minutes"),
        (4, "4 minutes"),
        (3, "3 minutes"),
        (2, "2 minutes"),
        (1, "1 minute"),
    ]

    SNEAK_COUNT_CHOICES = [(i, str(i)) for i in range(1, 6)] + [
        ("unlimited", "no limits")
    ]

    number_of_rounds = forms.ChoiceField(choices=NUMBER_OF_ROUNDS_CHOICES, initial=3)
    play_state_duration = forms.ChoiceField(
        choices=ROUND_DURATION_CHOICES, required=False, initial=15
    )
    create_state_duration = forms.ChoiceField(
        choices=SNEAK_CREATION_DURATION_CHOICES, required=False, initial=3
    )
    sneaks_per_round = forms.ChoiceField(choices=SNEAK_COUNT_CHOICES, initial="3")
    allow_additional_sneaks = forms.BooleanField(required=False, initial=True)

    def clean_sneaks_per_round(self):
        sneaks_per_round = self.cleaned_data.get("sneaks_per_round")
        if sneaks_per_round == "unlimited":
            return 0
        return sneaks_per_round

    class Meta:
        model = Game
        fields = [
            "game_name",
            "number_of_rounds",
            "play_state_duration",
            "sneaks_per_round",
            "allow_additional_sneaks",
            "create_state_duration",
        ]
        widgets = {
            "game_name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Game Name",
                    "maxlength": "32",
                }
            ),
            "number_of_rounds": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                }
            ),
            "play_state_duration": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                }
            ),
            "sneaks_per_round": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                }
            ),
            "create_state_duration": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                }
            ),
            "allow_additional_sneaks": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                }
            ),
        }


class RoundForm(forms.ModelForm):
    duration = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))

    class Meta:
        model = Round
        fields = ["duration"]


class MessageSender(forms.Form):
    word = forms.CharField(
        max_length=128,
        widget=forms.Textarea(  # Changed from TextInput to Textarea
            attrs={
                "class": "form-input block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50",
                "rows": 3,  # specify the number of rows
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


class StartGameForm(forms.Form):
    pass
