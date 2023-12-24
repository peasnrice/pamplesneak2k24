from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.dispatch import receiver


class ClearMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Clear messages if the user is logged in
        if request.user.is_authenticated:
            storage = messages.get_messages(request)
            storage.used = True
        return response


# Connect the signal to clear messages on login
@receiver(user_logged_in)
def clear_messages_on_login(sender, user, request, **kwargs):
    storage = messages.get_messages(request)
    storage.used = True
