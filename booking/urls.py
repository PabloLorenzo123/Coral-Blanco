from django.urls import path

from .views import RoomDetailView, SearchPageView

urlpatterns = [
    path('search/', SearchPageView.as_view(), name='search'),
    path('room_details/<uuid:uuid>', RoomDetailView.as_view(), name='room_detail'),
]