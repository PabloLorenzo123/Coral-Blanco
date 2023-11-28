from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm
# Create your views here.

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'