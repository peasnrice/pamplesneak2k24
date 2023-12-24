from allauth.account.forms import SignupForm, LoginForm
from django import forms


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        common_attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(common_attrs)
            self.fields["email"].widget = forms.HiddenInput()
            if field_name == "email":
                field.widget.attrs.update({"placeholder": "Email"})
            elif field_name == "username":
                field.widget.attrs.update({"placeholder": "Username"})
            elif field_name == "password1":
                field.widget.attrs.update({"placeholder": "Password"})
            elif field_name == "password2":
                field.widget.attrs.update({"placeholder": "Confirm Password"})


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        common_attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(common_attrs)
            if field_name == "login":
                field.widget.attrs.update({"placeholder": "Username"})
            elif field_name == "password":
                field.widget.attrs.update({"placeholder": "Password"})
            elif "remember" in self.fields:
                self.fields["remember"].widget = forms.CheckboxInput(
                    attrs={
                        "class": "form-checkbox h-5 w-5 text-gray-600"  # Tailwind classes for normal-sized checkbox
                    }
                )
