from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False  # Adjust as needed
    )

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "name",
            "last_name",
            "birthdate",
            "country",
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
            "name",
            "last_name",
            "birthdate",
            "country",
            "postcode",
            "phone_number",
            "country",
        )
