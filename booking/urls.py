from django.urls import path

from .views import RoomDetailView, search_room, reservate_now
urlpatterns = [
    path('room_details/<uuid:uuid>', RoomDetailView.as_view(), name='room_detail'),
    path('search_room/', search_room, name='search_room'),
    path('reservate_room/', reservate_now, name='reservate_room')
]