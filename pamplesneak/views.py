from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gameroom.forms import CreateGameForm, JoinGameForm
from django.contrib import messages


from pamplesneak.forms import CustomLoginForm, CustomSignupForm


# Returns Home Page from url /
def home(request):
    if request.user.is_authenticated:
        return redirect("start/")
    else:
        signup_form = CustomSignupForm()
        login_form = CustomLoginForm()
        return render(
            request,
            "login_or_register.html",
            {"signup_form": signup_form, "login_form": login_form},
        )


@login_required
def start(request):
    storage = messages.get_messages(request)
    for message in storage:
        if "logged in" in message.message:
            storage.used = True
    args = {}
    join_game_form = JoinGameForm()
    create_game_form = CreateGameForm()
    args["join_game"] = join_game_form
    args["create_game"] = create_game_form
    return render(request, "start.html", args)


from allauth.account.views import LoginView
