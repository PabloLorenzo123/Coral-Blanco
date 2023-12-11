"""This file is for the definition of the classes which will be used in search_results"""
from .models import Reservation
from django.shortcuts import get_object_or_404

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

"""This function creates a Reservation, and returns the object."""
def create_reservation(request, r_adults, r_children, r_check_in_date, r_check_out_date):
    Reservation.objects.create(
            user=request.user,
            adults = r_adults,
            children = r_children,
            check_in_date = r_check_in_date,
            check_out_date = r_check_out_date,
            )
    # print("User cart created")
    # Return the only reservation which isn't completed.
    return get_object_or_404(Reservation, user=request.user, completed=False)

"""This function, see all the reservations the user has. If he has a un uncompleted one it gets deleted, and a new one is created.
But the ones that were completed remain. At the end this return a Reservation object."""
def update_user_reservation_if_neccesary(request, r_adults, r_children, r_check_in_date, r_check_out_date):
    user_reservation = Reservation.objects.filter(user=request.user, completed=False)
    # If there exist an uncompleted reservation.
    if user_reservation.exists():
        # If the user has many reservations incompleted then we delete them.
        for reservation in user_reservation:
            reservation.delete()
        # then create a new reservation, and return the object.
        return create_reservation(request, r_adults, r_children, r_check_in_date, r_check_out_date)
    else:
        # If he doesn't have any then create a new one.
        return create_reservation(request, r_adults, r_children, r_check_in_date, r_check_out_date)
    
"""This function returns the current reservation instance."""
def return_reservation_object(request, uuid):
    return get_object_or_404(Reservation, user=request.user, completed=False, uuid=uuid)

