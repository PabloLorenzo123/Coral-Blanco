from django.urls import path

from .views import RoomDetailView, search_room
urlpatterns = [
    path('room_details/<uuid:uuid>', RoomDetailView.as_view(), name='room_detail'),
    path('search_room/', search_room, name='search_room'),
]