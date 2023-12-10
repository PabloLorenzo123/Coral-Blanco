from django.urls import path
from .views import HomePageView, GuestTest

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]