from typing import Any
from django.db.models.query import QuerySet
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import RoomType, Reservation, Guest, RoomReservations
from .forms import GuestForm
from .helper import RoomSearch, update_user_reservation_if_neccesary, return_reservation_object
import booking_project.settings as settings

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


"""This function is executed when the search room button is clicked, its job is to create a new reservation for the user
and display the rooms that are available.
- First you need to get the search room fields values, create a reservation with that data.
- Then look for each type of room, and check if it has the capacity requested.
- Then see if there're room available with no booking between the dates requested.
- Return a dictionary of all the rooms, indicating if they're available or not, and why."""  

@login_required  
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


# this can be a detailview.
@login_required
def reservate_now(request, uuid):
    # This is a post request, to add a room to the user's cart.
    # User needs to be logged in, and have a cart (which they're the owner of).
    user_reservation = return_reservation_object(request, uuid)
    # If return_reservation_object fails it will throw a 404.

    # 2. Set room_type of cart to be equal the one requested.
    user_reservation.room_type = RoomType.objects.get(
        type=request.POST.get('room_type_to_reservate')
        )
    user_reservation.save()

    # 3. We now need to set the info of the cart (total_price, taxes, nights)
    user_reservation.set_cart_info()
    print(user_reservation.uuid)

    context = {
        'user_reservation': user_reservation,
        }

    return render(request, 'booking/reservation_detail.html', context)


class CreateGuest(LoginRequiredMixin, generic.CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'booking/guest_details.html'  # Create an HTML template for the form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_reservation'] = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return context

    def get_success_url(self):
        user_reservation = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return reverse('confirm_reservation', kwargs={'uuid': user_reservation.uuid})

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
        # Check if the user already has a guest associated with their reservation.
        user_reservation = return_reservation_object(
            request=self.request, uuid=kwargs.get('uuid')) # This is the uuid at the end of the url.

        if Guest.objects.filter(user_reservation=user_reservation).exists():
            # In case the user's reservation already has a guest associated, let's update it.
            update_view_url = reverse('update_guest', kwargs={'uuid': kwargs.get('uuid')})
            return redirect(update_view_url)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Your form validation logic, e.g., saving the form data
        # Don't forget to add the cart field.
        user_reservation = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        # Create a new instance of the Guest model with form data
        guest_instance = form.save(commit=False)

        # Assign the user's reservation to the guest_instance
        guest_instance.user_reservation = user_reservation

        # Save the guest_instance to the database
        guest_instance.save()

        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)
    
class UpdateGuest(LoginRequiredMixin, generic.UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'booking/update_guest_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_reservation'] = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return context
    
    def get_success_url(self):
        user_reservation = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return reverse('confirm_reservation', kwargs={'uuid': user_reservation.uuid})

    def get_object(self):
        user_reservation = return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return Guest.objects.get(user_reservation=user_reservation)
    
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
        # Check if the user has a reservation, and if the reservation of this template is his.
        # This is the uuid at the end of the url.
        return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
        return super().dispatch(request, *args, **kwargs)


"""Confirm reservation"""
class ConfirmReservation(LoginRequiredMixin, generic.DetailView):
    model = Reservation
    template_name = "booking/confirm_reservation.html"
    context_object_name = "user_reservation"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_key'] = settings.STRIPE_TEST_PUBLISHABLE_KEY
        context['stripe_price'] = self.get_object().stripe_amount() # Because stripe price is in cents.
        return context
    
    def get_object(self):
        # Retrieve the cart specified in the url.
        return return_reservation_object(request=self.request, uuid=self.kwargs.get('uuid'))
    
    def dispatch(self, request, *args, **kwargs):
        user_reservation = self.get_object()
        # Check if the logged-in user is the owner of the cart
        if request.user != user_reservation.user:
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

The error can be either there's no room available, or the credit_card specified is invalid, or both.

"""
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
@login_required
def payment_confirm_reservation_done(request, uuid):   
    user_reservation = return_reservation_object(request, uuid)
    # Defining the context.
    context = {
        'user_reservation': user_reservation, 
        'guest_details': get_object_or_404(Guest, user_reservation=user_reservation), # This ensure there's a guest detail.
        }
    # Checking there's a room available before paying.
    if not user_reservation.room_type.is_there_room_available(user_reservation.check_in_date, user_reservation.check_out_date):
        user_reservation.delete()
        return HttpResponse('Ya no hay habitación disponible, intentelo denuevo.')
    
    """Payment"""
    # Try to process the payment.
    try:
        if request.method == 'POST':
            charge = stripe.Charge.create(
            amount= user_reservation.stripe_amount(),
            currency='usd',
            description='Reservar habitación' + user_reservation.room_type.type,
            source=request.POST['stripeToken'],
        )
        # Let's save the token of this transaction, so we can refund, and charge in the future.
        user_reservation.payment_token = charge.id
        user_reservation.card_last4 = charge.source['last4']
        user_reservation.card_brand = charge.source['brand']
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e.error.message}")
        return HttpResponse('No se pudo procesar el pago, intentelo denuevo.')
    
    """Room asignment"""
    # Assign room to the reservation.
    user_reservation.room = user_reservation.room_type.get_available_rooms(
        user_reservation.check_in_date, user_reservation.check_out_date
        )[0]
    # Complete the reservation. Once complete all the links behind are not accesible.
    # Create RoomReservation, to keep track the reservations of a room.
    RoomReservations.objects.create(
        room=user_reservation.room,
        reservation=user_reservation,
        check_in_date = user_reservation.check_in_date,
        check_out_date = user_reservation.check_out_date,
    )
    # Send confirmation email.
    user_reservation.send_confirmation_email()

 
    return render(request, 'booking/confirm_reservation_done.html', context)


"""User related views"""
class MyReservations(LoginRequiredMixin, generic.ListView):
    model = Reservation
    template_name = 'account/local/my_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

class ReservationDetail(LoginRequiredMixin, generic.DetailView):
    model = Reservation
    context_object_name = 'user_reservation'
    template_name = 'booking/confirmed_reservation_detail.html'

    def get_object(self):
        return get_object_or_404(Reservation, user=self.request.user, uuid=self.kwargs['uuid'], completed=True)
    
    def dispatch(self, request, *args, **kwargs):
        user_reservation = self.get_object()
        # Check if the logged-in user is the owner of the cart
        if request.user != user_reservation.user:
            return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)