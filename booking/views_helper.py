"""This file is for the definition of the classes which will be used in search_results"""
from .models import ReservationCart, Room, RoomType, RoomReservations
from django.db.models import Q

class RoomSearch:
    
    def __init__(self, room_type_object, room_fits, room_is_available=False):
        self.room_type_object = room_type_object # This is to reference each room in the template.
        self.room_fits = room_fits               # This indicates if the adults and children fit in this room.
        self.room_is_available = room_is_available # Are the rooms not booked for the requested date?
        
        self.define_availability_and_status()  # This will create the can_be_selected, and the proper message to show in the template.
    
    def define_availability_and_status(self):
        if self.room_fits and self.room_is_available:
            self.room_can_be_selected = True

        elif not self.room_fits:
            self.room_can_be_select = False
            self.status = "No se puede reservar esta habitación ya que excede el limite de " + "huéspedes de " + str(self.room_type_object.max_adults) + " adultos y " + str(self.room_type_object.max_children) + " niños"
        
        elif self.room_fits and not self.room_is_available:
            self.room_can_be_select = False
            self.status = "Esta habitación no se encuentra disponible"

def find_available_rooms(room_type, r_check_in_date, r_check_out_date):
    # This functions returns all the rooms of a roomtype available from checkin to checkout.
    return Room.objects.filter(
                type = room_type,
            ).exclude(
                room_id__in = RoomReservations.objects.filter(
                    Q(check_out_date__gt=r_check_in_date) & Q(check_in_date__lt=r_check_out_date))
                    .values('room_id')
            )

def update_user_cart_if_different(request, r_adults, r_children, r_check_in_date, r_check_out_date):
    user_cart_query = ReservationCart.objects.filter(user=request.user)
    if user_cart_query.exists():
        u_cart = user_cart_query[0] # This is to get the object.
        # If the user is making the same reservation request, we keep everything the same.
        if u_cart.adults == r_adults and u_cart.children == r_children and u_cart.check_in_date == r_check_in_date and u_cart.check_out_date == r_check_out_date:
            print("This cart remains unchanged")
        else:
            u_cart.adults, u_cart.children, u_cart.check_in_date, u_cart.check_out_date = r_adults, r_children, r_check_in_date, r_check_out_date
            u_cart.save()
            print("The user has already a cart, let's update it with the new info.")
    else:
        # Create a cart for this user, with the values requested.
         ReservationCart.objects.create(
            user=request.user,
            adults = r_adults,
            children = r_children,
            check_in_date = r_check_in_date,
            check_out_date = r_check_out_date,
            )
         print("User cart created")