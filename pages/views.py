from django.shortcuts import render
from django.views.generic import ListView, DetailView

from booking.models import RoomType

# Create your views here.
class HomePageView(ListView):
    model = RoomType
    template_name = 'home.html'
    context_object_name = 'room_types'

class RoomDetailView(DetailView):
    model = RoomType
    template_name = 'room_details.html'
    context_object_name = 'room'
    
