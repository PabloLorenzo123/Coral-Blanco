from django.urls import path
from .views import RoomDetailView, search_room, reservate_now, CreateGuest, UpdateGuest, ConfirmReservation

urlpatterns = [
    path('room_details/<uuid:uuid>', RoomDetailView.as_view(), name='room_detail'),
    path('search_room/', search_room, name='search_room'),
    path('reservate_room/<uuid:uuid>/', reservate_now, name='reservate_room'), # The uuid means to the cart identifier.
    path('guest_details/<uuid:uuid>/', CreateGuest.as_view(), name='guest_details'), # The uuid is the cart indentifier.
    path('update_guest/<uuid:uuid>/', UpdateGuest.as_view(), name='update_guest'), # The uuid is the cart indentifier.
    path('confirm_reservation/<uuid:uuid>/', ConfirmReservation.as_view(), name='confirm_reservation'),
]