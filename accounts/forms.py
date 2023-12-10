from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from allauth.account.forms import SignupForm

# THIS FORM IS USED IN MY INFORMATION.HTML
class CustomUserChangeForm(UserChangeForm):
    birthdate = forms.DateField( widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    name = forms.CharField(max_length=30, label='Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    country = forms.CharField(max_length=30, label='Country', required=True)
    phone_number = forms.CharField(max_length=15, label='Phone number', required=False)
    city = forms.CharField(max_length=50, label='City', required=False)
    postcode = forms.CharField(max_length=10, label='post_code', required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "name",
            "last_name",
            "birthdate", # it works if i delete this.
            "address",
            "country",
            "phone_number",
            "city",
            "postcode",
        )

"""Allauth"""
# extend the standard signup form, and add it to settings.
class CustomSignupForm(SignupForm):

    email = forms.EmailField(max_length=255, label='Email')
    name = forms.CharField(max_length=30, label='Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Birthdate')
    country = forms.CharField(max_length=30, label='Country')

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'last_name', 'birthdate', 'country', 'password1', 'password2')

# THIS FORM IS NOT USED.
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
