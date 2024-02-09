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


@csrf_exempt
@login_required
def save_subscription(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            subscription_data = json.dumps(data)

            # Check if this exact subscription already exists to avoid duplicates
            existing_subscription = PushSubscription.objects.filter(
                user=user, subscription_json=subscription_data
            ).first()

            if not existing_subscription:
                # If it doesn't exist, create a new subscription
                PushSubscription.objects.create(
                    user=user, subscription_json=subscription_data
                )

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})


@csrf_exempt
@login_required
def update_or_save_subscription(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        subscription, created = PushSubscription.objects.update_or_create(
            user=user, defaults={"subscription_json": json.dumps(data)}
        )
        if created:
            return JsonResponse(
                {"success": True, "message": "Subscription saved."}, status=201
            )
        else:
            return JsonResponse(
                {"success": True, "message": "Subscription updated."}, status=200
            )
    return JsonResponse({"error": True, "message": "Invalid request"}, status=400)
