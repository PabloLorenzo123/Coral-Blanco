from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views import generic
from django.db.models import Q
from .views_helper import RoomSearch

from .models import RoomType, Room, ReservationCart, RoomReservations

# Create your views here.
class RoomDetailView(generic.DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'

    def get_object(self):
        # UpdateUser view is expecting a primary key (pk) or slug in the URL, but it's not receiving it.
        # I'm updating the get_object method so it uses the uuid instead of the pk.
        return RoomType.objects.get(uuid=self.kwargs['uuid'])
    
class RoomsListView(generic.ListView):
    model = RoomType
    template_name = 'rooms.html'
    context_object_name = 'room_types'
    
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
    available_room_types = {'room_types': []} 

    for room_type in RoomType.objects.all():

        if room_type.max_adults >= r_adults and room_type.max_children >= r_children:
            room_type_fits = True # this means that this type of room can fit this many people.
            room_type_available = False # This is to check if there are rooms available for this type.

            # We now need to check, if there rooms available for this type of room.
            available_rooms = Room.objects.filter(
                type = room_type,
            ).exclude(
                room_id__in = RoomReservations.objects.filter(
                    Q(check_out_date__gt=r_check_in_date) & Q(check_in_date__lt=r_check_out_date))
                    .values('room_id')
            )
            # If there is room available for this type.
            if len(available_rooms) > 0:
                room_type_available = True
            
            # If the type applies for the amount of people, and it's available show in the listview as normal.
            # If the room type apllies for the amount of people, but there are not rooms available, show 'habitación no disponible'
            available_room_types['room_types'].append(
                RoomSearch(room_type_object=room_type, room_fits=room_type_fits, room_is_available=room_type_available)
            )
        else:
            # If the amount of people exceds the capicity, then show 'No se puede seleccionar esta habitación porque excede la capacidad permitida'.
            available_room_types['room_types'].append(
                RoomSearch(room_type_object=room_type, room_fits=False, room_is_available=False)
            )
    print(available_room_types['room_types'])
    # This return will send to the template a dictionary which have the [RoomTypeObject, it_fits?, RoomAvailable]
    return render(request, 'booking/search_results.html', available_room_types)
