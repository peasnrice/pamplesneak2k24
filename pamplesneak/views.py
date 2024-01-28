from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gameroom.forms import CreateGameForm, JoinGameForm
from django.contrib import messages
from pywebpush import webpush, WebPushException
from pamplesneak.forms import CustomLoginForm, CustomSignupForm
from django.conf import settings
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import PushSubscription
from django.shortcuts import get_object_or_404

import json


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
    args = {
        "join_game": JoinGameForm(),
        "create_game": CreateGameForm(),
        "VAPID_PUBLIC_KEY": settings.VAPID_PUBLIC_KEY,  # Add this line
    }
    return render(request, "start.html", args)


from allauth.account.views import LoginView


def send_web_push(subscription_information, message):
    try:
        response = webpush(
            subscription_info=subscription_information,
            data=message,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"},
        )
        return response.json()
    except WebPushException as ex:
        # Handle the exception as you see fit (e.g., log it, retry mechanism, etc.)
        print(f"Web push failed: {ex}")


@login_required
def send_push_notification(request):
    try:
        # Get the authenticated user's subscription information
        user = request.user
        push_subscription = get_object_or_404(PushSubscription, user=user)

        subscription_information = json.loads(
            push_subscription.subscription_json
        )  # Load JSON from the database

        message = json.dumps(
            {
                "title": "Notification Title",
                "body": "This is a server-side push notification!",
            }
        )

        print(subscription_information)

        response = webpush(
            subscription_info=subscription_information,
            data=message,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"},
        )
        return JsonResponse(
            {"status": "success", "message": "Push notification sent successfully."}
        )
    except Exception as ex:
        # Handle any exceptions (e.g., invalid subscription data, webpush exceptions, etc.)
        return JsonResponse({"status": "error", "message": str(ex)})


@csrf_exempt
@login_required
def save_subscription(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Get the authenticated user
            user = request.user

            # Check if the user already has a subscription, and update it if necessary
            subscription, created = PushSubscription.objects.get_or_create(user=user)
            subscription.subscription_json = json.dumps(
                data
            )  # Store subscription data as JSON
            subscription.save()

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
