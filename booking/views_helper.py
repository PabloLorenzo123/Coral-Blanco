"""This file is for the definition of the classes which will be used in search_results"""
from .models import ReservationCart, Room, RoomType, RoomReservations
from django.db.models import Q

class RoomSearch:
    
    def __init__(self, room_type_object, room_fits, room_is_available):
        self.room_type_object = room_type_object
        self.room_fits = room_fits
        self.room_is_available = room_is_available
        
        self.define_availability_and_status()
    
    def define_availability_and_status(self):
        if self.room_fits and self.room_is_available:
            self.room_can_be_selected = True

        elif not self.room_fits:
            self.room_can_be_select = False
            self.status = "No se puede reservar esta habitación ya que excede el limite de " + "huéspedes de " + str(self.room_type_object.max_adults) + " adultos y " + str(self.room_type_object.max_children) + " niÑos"
        
        elif self.room_fits and not self.room_is_available:
            self.room_can_be_select = False
            self.status = "Esta habitación no se encuentra disponible"

def find_available_rooms(room_type, r_check_in_date, r_check_out_date):
    # This functions returns all the rooms of a roomtype available from checkin to checkout.
    return Room.objects.filter(
                type = room_type,
                space_taken = False,
            ).exclude(
                room_id__in = RoomReservations.objects.filter(
                    Q(check_out_date__gt=r_check_in_date) & Q(check_in_date__lt=r_check_out_date))
                    .values('room_id')
            )

def reset_user_cart_if_exists(request):
    user_cart = ReservationCart.objects.filter(user=request.user)
    if user_cart.exists():
        if user_cart[0].room:
            user_cart[0].room.space_taken = False
            user_cart[0].room.save()

            user_cart[0].room = None
            user_cart[0].save()

def delete_user_cart_if_exists(request):
    user_cart = ReservationCart.objects.filter(user=request.user)
    if user_cart.exists():
        if user_cart[0].room:
            user_cart[0].room.space_taken = False
            user_cart[0].room.save()

            user_cart[0].room = None
            user_cart[0].save()

        user_cart[0].delete()
        print("Just deleted a cart from this user!")