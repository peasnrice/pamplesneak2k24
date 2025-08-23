from users.models import PushSubscription
from pywebpush import webpush, WebPushException
from django.conf import settings
import json
from celery import shared_task


@shared_task
def send_push_notification(user_id, payload):
    # Fetch all subscription information for the user
    subscriptions = PushSubscription.objects.filter(user_id=user_id)

    if not subscriptions.exists():
        print(f"No subscriptions found for user {user_id}")
        return

    # Prepare the push notification payload
    notification_data = json.dumps(
        {
            "notification": {
                "title": payload["title"],
                "body": payload["message"],
                "icon": "path/to/icon.png",
                "click_action": payload["url"],
            }
        }
    )
    print("notification payload")
    print(notification_data)

    # Iterate over all subscriptions and send the notification
    for subscription in subscriptions:
        try:
            subscription_info = json.loads(subscription.subscription_json)

            webpush(
                subscription_info=subscription_info,
                data=notification_data,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}",
                },
            )
        except WebPushException as e:
            print(f"Web push failed for subscription {subscription.id}: {e}")
            # Optionally, handle the failed subscription (e.g., delete or mark as inactive)
