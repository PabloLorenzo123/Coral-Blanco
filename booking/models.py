from django.db import models
import uuid
from accounts.models import CustomUser
from django.db.models import Q

# Create your models here.


"""Room and Images"""
class RoomType(models.Model):
    room_type_id = models.AutoField(primary_key=True) # to save space with foreign keys.

    uuid = models.UUIDField( # For displaying detailview without exposing the database.
        default = uuid.uuid4,
        editable = False,
        unique = True,
    )

    type = models.CharField(max_length=255, unique=True)
    # With RoomType.objects[x].images can acces its images.
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField()

    max_adults = models.IntegerField(blank=True, null=True)
    max_children = models.IntegerField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def get_available_rooms(self, r_check_in_date, r_check_out_date):
        return Room.objects.filter(
                type = self.room_type_id,
            ).exclude(
                room_id__in = RoomReservations.objects.filter(
                    Q(check_out_date__gt=r_check_in_date) & Q(check_in_date__lt=r_check_out_date))
                    .values('room_id')
            )
    
    def is_there_room_available(self, r_check_in_date, r_check_out_date):
        return len(self.get_available_rooms(r_check_in_date, r_check_out_date)) > 0
    
    def __str__(self):
        return self.type

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)

    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True
    )
    number = models.IntegerField(null=False) # Number identifies floor.
    building = models.IntegerField(default=1)

    avaliability = models.BooleanField(default=True)

    # When a user reserves a room, but it hasnt been confirmed this becomes True, so no one else steals the room.
    # When the reservation is confirmed that this will return to false.

    type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="room_type",
    )

    def __str__(self):
        return str(self.number)


    
class Image(models.Model):
    room_type = models.ForeignKey(
        RoomType,
        related_name="images",
        on_delete=models.CASCADE,
    )

    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True
    )
    image = models.ImageField(upload_to='rooms/', blank=True)
    alt = models.CharField(max_length=255)

    def __str__(self):
        return self.alt

"""Reservation and cart"""
# All Users have a unique cart.
# we have to make sure everytime a user signup they have a cart.
# We can do this checking before making the search check if the user has a cart if he doesnt create one then.
# When user clicks search if he has already a cart we delete it, then create one.
# If he doesnt have a cart we create one, with a unique identifier which could be the reservation number.

"""ReservationCart means the cart of a reservation that is in progress but has not been paid or confirmed"""
class ReservationCart(models.Model):
    id = models.AutoField(primary_key=True)
    
    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True,
        null=True
    ) # With this we keep track of the user_cart in the urls.

    # With the combination of an UUID and the guest name we'll create the identifier.
    reservation_confirmation_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    unique_identifier = models.CharField(70, null=True)

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        related_name="cart",
        unique=True,
        editable=False,
        null=False,
    ) # This way the user can acces its cart with user.cart.

    adults = models.IntegerField(null=True, default=0)
    children = models.IntegerField(null=True, default=0)
    check_in_date = models.DateField(null=False)
    check_out_date = models.DateField(null=False)

    nights = models.IntegerField(null=True)

    reservation_price = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    taxes = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    total_price = models.DecimalField(decimal_places=2, max_digits=8, null=True)

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        null=True,
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        null=True,
    )

    completed = models.BooleanField(default=False)

    def set_cart_info(self):
         self.nights = (self.check_out_date - self.check_in_date).days - 1
         self.reservation_price = float(self.nights * self.room_type.price)
         self.taxes = float(self.reservation_price) * 0.20 # HERE DEFINE A TAXES CALCULATOR!
         self.total_price = self.reservation_price + self.taxes
         self.save()
    
    def create_unique_identifier(self):
        self.unique_identifier = f"{self.guest.country}{self.reservation_confirmation_uuid}-{self.guest.name}"
    
    def __str__(self):
        return f"Cart of {self.user.name}\nNights: {self.nights}\nPrice: {self.reservation_price}\nTaxes: {self.taxes}\nTotal: {self.total_price}" 

# This table will relate to the user cart, it contains the guest info and card info.
class Guest(models.Model):
    user_cart = models.OneToOneField(
        ReservationCart,
        related_name='guest',
        on_delete=models.CASCADE,
        editable=False,
        null=True,
    )

    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True)

    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)  # Adjust max_length based on your requirements
    card_number = models.CharField(max_length=16)  # Assuming a typical credit card number length
    expire_date = models.CharField(max_length=7)   # Assuming MM/YYYY format for expiration date
    csv = models.CharField(max_length=4)           # Assuming a typical CSV length

    def __str__(self):
        return f'{self.name} {self.last_name}'
    

"""Room Reservations refers to the tables that contain all the reservations that have been made to a room."""
class RoomReservations(models.Model):
    id = models.AutoField(primary_key=True)

    
    room = models.ForeignKey(
        Room, on_delete = models.CASCADE,
    ) # with this we can know the type, and price.

    adults = models.IntegerField()
    children = models.IntegerField()

    total_price = models.IntegerField() # This will be equal to price * day/night.

    cart = models.ForeignKey(
        ReservationCart, on_delete=models.CASCADE,
        related_name='room_reserved',
    )
    
    check_in_date = models.DateField(null=True)
    check_out_date = models.DateField(null=True) # remember to add null false.
