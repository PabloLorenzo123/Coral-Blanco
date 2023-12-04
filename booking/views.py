from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse

from .models import RoomType, ReservationCart, Guest, RoomReservations
from .forms import GuestForm
from .views_helper import RoomSearch, update_user_reservation_if_neccesary
from .confirm_reservation_helper import charge_card, send_confirmation_email

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

    # Create a reservation.
    user_reservation = update_user_reservation_if_neccesary(request, r_adults, r_children, r_check_in_date, r_check_out_date)

    # Now find what type of rooms can have this many guests, and if they are available.
    context = {'room_types': [], 'user_reservation': user_reservation} 

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

# logged in mixin.
# this can be a detailview.
def reservate_now(request, uuid):
    # This is a post request, to add a room to the user's cart.
    # User needs to be logged in, and have a cart (which they're the owner of).
    user_cart_query = ReservationCart.objects.filter(user=request.user, uuid=uuid)
    if not user_cart_query.exists():
        print("This user doesn't pass the testt")
    
    user_cart = user_cart_query[0] # because filter returns a queryset and not an object.

    # 2. Set room_type of cart to be equal the one requested.
    room_type_name = request.POST.get('room_type_to_reservate')
    room_type = RoomType.objects.filter(type=room_type_name)[0] # We do this to get the object of the class.

    user_cart.room_type = room_type
    user_cart.save()

    # 3. We now need to set the info of the cart (total_price, taxes, nights)
    user_cart.set_cart_info()
    print(user_cart)

    context = {
        'user_cart': user_cart,
        }

    return render(request, 'booking/cart_detail.html', context)

class CreateGuest(generic.CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'booking/guest_details.html'  # Create an HTML template for the form

    def get_success_url(self):
        user_cart = self.request.user.cart
        return reverse('confirm_reservation', kwargs={'uuid': user_cart.uuid})

    def get_initial(self):
        # This way the form gets initial values that could haven provided before in the user account, in user_info.
        form_context = super().get_initial()
        form_context['name'] = self.request.user.name
        form_context['last_name'] = self.request.user.last_name
        form_context['email'] = self.request.user.email
        form_context['country'] = self.request.user.country
        form_context['postal_code'] = self.request.user.postcode
        return form_context
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user already has a guest associated with their cart
        cart = ReservationCart.objects.get(uuid=kwargs.get('uuid')) # This is the uuid at the end of the url.

        if Guest.objects.filter(user_cart=cart).exists():
            # In case the user's cart already has a guest associated, let's update it.
            update_view_url = reverse('update_guest', kwargs={'uuid': kwargs.get('uuid')})
            return redirect(update_view_url)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Your form validation logic, e.g., saving the form data
        # Don't forget to add the cart field.

        # Create a new instance of the Guest model with form data
        guest_instance = form.save(commit=False)

        # Assign the user's cart to the guest_instance
        guest_instance.user_cart = self.request.user.cart

        # Save the guest_instance to the database
        guest_instance.save()

        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)
    
class UpdateGuest(generic.UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'booking/update_guest_details.html'

    def get_success_url(self):
        user_cart = self.request.user.cart
        return reverse('confirm_reservation', kwargs={'uuid': user_cart.uuid})

    def get_object(self):
        user_cart = ReservationCart.objects.get(uuid = self.kwargs['uuid'])
        return Guest.objects.get(user_cart=user_cart)
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user has a cart, and if the cart of this template is his.
        get_object_or_404(ReservationCart, uuid=self.request.user.cart.uuid) # This is the uuid at the end of the url.

        return super().dispatch(request, *args, **kwargs)

class ConfirmReservation(generic.DetailView):
    model = ReservationCart
    template_name = "booking/confirm_reservation.html"
    context_object_name = "reservation"
    success_url = ''
    
    def get_object(self):
        # Retrieve the cart specified in the url.
        return get_object_or_404(ReservationCart, uuid=self.kwargs['uuid'])
    
    def dispatch(self, request, *args, **kwargs):
        reservation_cart = self.get_object()
        # Check if the logged-in user is the owner of the cart
        if request.user != reservation_cart.user:
            return HttpResponseForbidden("You do not have permission to view this page.")

        return super().dispatch(request, *args, **kwargs)
    
"""Confirm_reservation_done, is used when the the confirm button is clicked on the last template
This function needs to send a html email, with the details of the reservation to the email specified 
in the guest (which is related to the ReservationCart table).

- 1. Need to check first that there's still room available. If so the reservation was succesful, if not it was unsuccesful.
- 2. Then we need to charge 0$ dollars to the credit_card specified to see if it's valid, if the transaction is succesful, then proceed.
- 3. Then assign a room to the reservation, which will be saved in the ReservationCart.
- 4. When the reservation is completed, we assign the value completed=true, so when a user gets to make a new reservation he does on another.
instance.
- 5. Send the html confirmation email.

the return template is a template which confirms everything went smooth. If there's an error we'll notify it.

The error can't be either there's no room available, or the credit_card specified is invalid, or both.

"""

def confirm_reservation_done(request, uuid):
    reservation = get_object_or_404(ReservationCart, uuid=uuid)
    context = {
        'reservation': reservation, 
        'guest_details': get_object_or_404(Guest, user_cart=reservation), # This ensure there's a guest detail.
            }
    success = True

    if reservation.user != request.user or reservation != request.user.cart:
        return HttpResponseForbidden('No eres el dueÑo de esta reservación')
    
    if not reservation.room_type.is_there_room_available(reservation.check_in_date, reservation.check_out_date):
        success = False
        reservation.delete()
        return HttpResponse('Ya no hay habitación disponible, intentelo denuevo.')
    
    # Charge the $0 dollars to the guest account.
    if not charge_card(request):
        success = False
        reservation.delete()
        return HttpResponse('La información bancaria ofrecida no es valida, intentelo denuevo.')
    # Assign room to the reservation.
    reservation.room = reservation.room_type.get_available_rooms(reservation.check_in_date, reservation.check_out_date)[0]
    # Complete the reservation. Once complete all the links behind are not accesible.
    reservation.completed = True
    reservation.create_unique_identifier()
    reservation.save()
    # Create RoomReservation, to keep track the reservations of a room.
    RoomReservations.objects.create(
        room=reservation.room,
        reservation=reservation,
        check_in_date = reservation.check_in_date,
        check_out_date = reservation.check_out_date,
    )
    # Send email.
    send_confirmation_email(request, reservation)

    return render(request, 'booking/confirm_reservation_done.html', context)
    return HttpResponse('La reservación ha sido exitosa, revise su correo para que vea su confirmación.')