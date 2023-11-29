from django.urls import path

from .views import RoomDetailView

urlpatterns = [
    path('<uuid:pk>', RoomDetailView.as_view(), name='room_detail'),
]