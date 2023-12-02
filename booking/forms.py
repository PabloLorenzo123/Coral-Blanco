from .models import Guest
from django import forms

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = '__all__'