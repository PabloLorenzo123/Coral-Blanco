from django.shortcuts import render
from django.views import generic

from .models import RoomType, Room

# Create your views here.
class RoomDetailView(generic.DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'

def SearchRoom(request):
    print(request.GET.get('rooms'))
    print(request.GET.get('adults'))
    print(request.GET.get('children'))
    # First know what types of room, can every room get. for example 1 guest can fit in all rooms.
    # Second look through each type of room and find what rooms are free from x day to y day.
        # Select * FROM Rooms
        # WHERE type = current_type
        # AND room_id NOT IN (
        # SELECT room_id FROM reservations
        # WHERE check_out_date > 'desired_check_in_date'
        # AND check_in_date < 'desired_check_out_date' )
        # if rooms_found > 0:
            # then dict['room_type'] = True
        # show in webpage all the room types available.
        # when the user chooses one room, then save it to the reservation cart.
        # ask if wanna book another room.
           # if so repeat the cycle.
        # else
         # go to checkout.