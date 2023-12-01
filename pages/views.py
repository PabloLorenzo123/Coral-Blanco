from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView

from booking.models import RoomType

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'home.html'

class SearchPageView(ListView):
    model = RoomType
    template_name = 'home.html'
    context_object_name = 'room_types'
    
