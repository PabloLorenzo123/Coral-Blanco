from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from .models import CustomUser
from django.contrib.auth.mixins import UserPassesTestMixin
from allauth.account.views import SignupView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


from .forms import CustomUserChangeForm
# Create your views here.

class PrivateArea(LoginRequiredMixin, generic.TemplateView):
    template_name = 'account/local/private_area.html'

"""Extending allauth signup view to use my form, and redirect to home"""
class CustomSignupView(SignupView):
    success_url = reverse_lazy('home')  # Set your home URL or any other desired URL

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        response = super().form_valid(form)
        # Additional logic if needed
        return response

# Because allauth doesn't provide it, i'm defining it.
class UpdateUser(UserPassesTestMixin, generic.UpdateView):
    form_class = CustomUserChangeForm
    model = CustomUser
    template_name = "account/local/update_user.html"
    

    def get_object(self):
        # UpdateUser view is expecting a primary key (pk) or slug in the URL, but it's not receiving it.
        # I'm updating the get_object method so it uses the uuid instead of the pk.
        return CustomUser.objects.get(uuid=self.kwargs['uuid'])
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial['name'] = user.name
        initial['last_name'] = user.last_name
        initial['birthdate'] = str(user.birthdate)
        initial['country'] = user.country
        initial['city'] = user.city
        initial["postcode"] = user.postcode
        initial['phone_number'] = user.phone_number
        # Add other fields as needed
        return initial
    
    def test_func(self):
        # Check if the requesting user is the same as the user being updated
        return self.request.user == self.get_object()
    
    def form_valid(self, form_class):
        print("form is valid")
        return super().form_valid(form_class)

    def form_invalid(self, form_class):
        print("form invalid")
        print(form_class.errors)
        return super().form_invalid(form_class)
