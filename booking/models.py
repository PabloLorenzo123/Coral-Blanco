from django.db import models
import uuid
from accounts.models import CustomUser

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

    space_taken = models.BooleanField(default=False)
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

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        related_name="cart",
        unique=True,
        editable=False,
        null=False,
    )

    check_in_date = models.DateField(null=False)
    check_out_date = models.DateField(null=False)

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        null=True,
    )
    # This way the user can acces its cart with user.cart.

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
