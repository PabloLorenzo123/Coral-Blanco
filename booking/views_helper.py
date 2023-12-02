"""This file is for the definition of the classes which will be used in search_results"""

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
            self.status = "No se puede reservar esta habitación ya que excede el limite de " + "huéspedes de " + str({self.room_type_object.max_adults}) + " adultos y " + str({self.room_type_object.max_children}) + " niÑos"
        
        elif self.room_fits and not self.room_is_available:
            self.room_can_be_select = False
            self.status = "Esta habitación no se encuentra disponible"
        