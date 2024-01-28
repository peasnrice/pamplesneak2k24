from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PushSubscription


class CustomUserAdmin(UserAdmin):
    # If your CustomUser model includes new fields, you might want to display them in the admin.
    # You can add these fields to list_display, fieldsets, and add_fieldsets
    model = CustomUser
    list_display = [
        "email",
        "username",
        "nickname",
        "phone_number",
        "is_staff",
    ]

    # If you've added new fields to CustomUser, you might need to add fieldsets for them
    fieldsets = UserAdmin.fieldsets + (
        # Add your custom fields in a new section titled "Custom Fields"
        (
            "Custom Fields",
            {
                "fields": (
                    "nickname",
                    "phone_number",
                )
            },
        ),
    )

    # Adjust this if you've added new fields and want them to be editable when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Custom Fields",
            {
                "fields": (
                    "nickname",
                    "phone_number",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PushSubscription)
