from django.urls import path

from .views import RoomDetailView, SearchRoom
urlpatterns = [
    path('<uuid:pk>', RoomDetailView.as_view(), name='room_detail'),
    path('search_room/', SearchRoom, name='search_room'),
]