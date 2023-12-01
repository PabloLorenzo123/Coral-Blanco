from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import RoomType

# Create your views here.
class RoomDetailView(DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'

    def get_object(self):
        # UpdateUser view is expecting a primary key (pk) or slug in the URL, but it's not receiving it.
        # I'm updating the get_object method so it uses the uuid instead of the pk.
        return RoomType.objects.get(uuid=self.kwargs['uuid'])
    
class SearchPageView(ListView):
    model = RoomType
    template_name = 'search.html'
    context_object_name = 'room_types'