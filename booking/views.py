from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views import generic
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

from .models import RoomType, Room, ReservationCart, RoomReservations, Guest
from .forms import GuestForm
from .views_helper import RoomSearch, update_user_cart_if_different, find_available_rooms

# Create your views here.
class RoomDetailView(generic.DetailView):
    model = RoomType
    template_name = 'booking/room_detail.html'
    context_object_name = 'room'

    def get_object(self):
        # UpdateUser view is expecting a primary key (pk) or slug in the URL, but it's not receiving it.
        # I'm updating the get_object method so it uses the uuid instead of the pk.
        return RoomType.objects.get(uuid=self.kwargs['uuid'])

    
def search_room(request):
    # first check the user is logged in, with @loginrequired.
    r_adults = int(request.GET.get('adults'))
    r_children = int(request.GET.get('children'))
    r_check_in_date = request.GET.get('check_in_date')
    r_check_out_date = request.GET.get('check_out_date')

    # check if he has a cart, if it's the same reservation keep the cart the same, if its different update the cart, if he doesnt have one create one.
    update_user_cart_if_different(request, r_adults, r_children, r_check_in_date, r_check_out_date)

    # Now find what type of rooms can have this many guests, and if they are available.
    context = {'room_types': []} 

    for room_type in RoomType.objects.all():

        if r_adults <= room_type.max_adults and r_children <= room_type.max_children:
            # See if there is an available room.
            room_type_available= room_type.is_there_room_available(r_check_in_date, r_check_out_date)
            # If the type applies for the amount of people, and it's available show in the listview as normal.
            # If the room type apllies for the amount of people, but there are not rooms available, show 'habitación no disponible'
            context['room_types'].append(
                RoomSearch(room_type_object=room_type, room_fits=True, room_is_available=room_type_available)
            )
        else:
            # If the amount of people exceds the capicity, then show 'No se puede seleccionar esta habitación porque excede la capacidad permitida'.
            context['room_types'].append(
                RoomSearch(room_type_object=room_type, room_fits=False)
            )

    # This return will send to the template a dictionary which of objects which have the type of room, and if their avaliability.
    return render(request, 'booking/search_results.html', context)


def reservate_now(request):
    # This is a post request, to add a room to the user's cart.
    # User needs to be logged in, and have a cart.
    user_cart_query = ReservationCart.objects.filter(user=request.user)

    # To pass the test you need to be logged in, have a cart.
    if not request.user.is_authenticated or not user_cart_query.exists():
        # redirect to home.
        print("User doesn't have a cart, he can't reservate")
        return
    
    user_cart = user_cart_query[0] # because filter returns a queryset and not an object.

    # 2. Set room_type of cart to be equal the one requested.
    room_type_name = request.POST.get('room_type_to_reservate')
    room_type = RoomType.objects.filter(type=room_type_name)[0] # We do this to get the object of the class.

    user_cart.room_type = room_type
    user_cart.save()

    print(user_cart.room_type)

    #3. Now we have to calculate the total price.
    user_cart.nights = (user_cart.check_out_date - user_cart.check_in_date).days - 1
    user_cart.reservation_price = float(user_cart.nights * user_cart.room_type.price)
    user_cart.taxes = float(user_cart.reservation_price) * 0.20 # HERE DEFINE A TAXES CALCULATOR!
    user_cart.total_price = user_cart.reservation_price + user_cart.taxes
    user_cart.save()

    context = {
        'user_cart': user_cart,
        }

    return render(request, 'booking/cart_detail.html', context)

class CreateGuest(generic.CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'booking/guest_details.html'  # Create an HTML template for the form
    success_url = '/success/' 