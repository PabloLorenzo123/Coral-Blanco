from django.shortcuts import render
from django.views import generic
from django.db.models import Q

from .models import RoomType, Room, ReservationCart, RoomReserved

# Create your views here.
class RoomDetailView(generic.DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'

def search_room(request):
    # first check the user is logged in, with @loginrequired.
    r_adults = int(request.GET.get('adults'))
    r_children = int(request.GET.get('children'))
    r_check_in_date = request.GET.get('check_in_date')
    r_check_out_date = request.GET.get('check_out_date')

    # check if he has a cart.
    if ReservationCart.objects.filter(user=request.user).exists():
        # if he has one delete it.
        ReservationCart.objects.filter(user=request.user).delete()
        print("This user already has a cart!, lets delete it!")

    # Then create a new cart for this user.
    ReservationCart.objects.create(
            user=request.user,
            check_in_date = r_check_in_date,
            check_out_date = r_check_out_date,
    )
    print("Just created a new cart for this user!")

    # Now find what type of rooms can have this many guests, and if they are available.
    available_room_types = {} 

    for room_type in RoomType.objects.all():
        if room_type.max_adults >= r_adults and room_type.max_children >= r_children:
            room_type_applies = True # this means that this type of room can fit this many people.
            room_type_available = False # This is to check if there are rooms available for this type.

            # We now need to check, if there rooms available for this type of room.
            available_rooms = Room.objects.filter(
                type = room_type,
            ).exclude(
                room_id__in = RoomReserved.objects.filter(
                    Q(check_out_date__gt=r_check_in_date) & Q(check_in_date__lt=r_check_out_date))
                    .values('room_id')
            )

            if len(available_rooms) > 0:
                room_type_available = True
            
            # If the type applies for the amount of people, and it's available show in the listview as normal.
            # If the room type apllies for the amount of people, but there are not rooms available, show 'habitación no disponible'
            available_room_types[room_type] = [room_type_applies, room_type_available]
        else:
            # If the amount of people exceds the capicity, then show 'No se puede seleccionar esta habitación porque excede la capacidad permitida'.
            available_room_types[room_type] = [False, False]
    
    print('available rooms = ' + str(available_room_types))

    # Check if the types available
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