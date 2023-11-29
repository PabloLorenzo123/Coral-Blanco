from django.shortcuts import render
from django.views.generic import DetailView

from .models import RoomType

# Create your views here.
class RoomDetailView(DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'