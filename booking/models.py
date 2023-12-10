from django.db import models
import uuid
from accounts.models import CustomUser
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
import booking_project.settings as settings
from django.template.loader import render_to_string

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
    # With RoomType.objects[x].images can access its images.
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

    @staticmethod
    def csv_file_name():
        return 'Room_Types'
    
    @staticmethod
    def csv_headers():
        return ['Type', 'Short Description', 'Description', 'Max Adults', 'Max Children', 'Price']
    
    @staticmethod
    def csv_attributes():
        return ['', 'short_description','description', 'max_adults', 'max_children']
    
    def __str__(self):
        return self.type

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)

    number = models.IntegerField(null=False) # Number identifies floor.

    type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="room_type",
    )

    @staticmethod
    def csv_file_name():
        return 'Rooms'
    
    @staticmethod
    def csv_headers():
        return ['Number', 'Building', 'Avaliability', 'Type']
    
    @staticmethod
    def csv_attributes():
        return ['number', 'building', 'availability', 'room_type']
    
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

class Feature(models.Model):
    feature = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, default="")
    
    def __str__(self):
        return self.feature

class RoomFeature(models.Model):
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='features'
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='room_types'
    )


"""Reservation"""
class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)

    # With the combination of an UUID and the guest name we'll create the identifier.
    reservation_confirmation_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    unique_identifier = models.CharField(max_length=70, null=True)

    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True,
    ) # With this we keep track of the user_cart in the urls.

    user = models.ForeignKey(
        CustomUser,
        related_name="cart",
        editable=False,
        on_delete=models.CASCADE,
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
    """Stripe"""
    # Stripe payment token, with this token we can refund and charge in the future.
    card_payment_token = models.CharField(max_length=100, null=True)
    card_last4 = models.CharField(max_length=4, null=True)
    card_brand = models.CharField(max_length=10, null=True)

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

    """This set's the reservation information, as its price, its taxes and calculates total price."""
    def set_cart_info(self):
         self.nights = (self.check_out_date - self.check_in_date).days - 1
         self.reservation_price = float(self.nights * self.room_type.price)
         self.taxes = float(self.reservation_price) * 0.20 # HERE DEFINE A TAXES CALCULATOR!
         self.total_price = self.reservation_price + self.taxes
         self.save()

    """This creates a unique identifier for the reservation."""
    def create_unique_identifier(self):
        self.unique_identifier = f"{self.guest.country}{self.reservation_confirmation_uuid}-{self.guest.name}"

    """Sends the confirmation email, this is the last step in a reservation."""
    def send_confirmation_email(self):
        # First create an identifier.
        self.create_unique_identifier()
        self.save()
        html_content = render_to_string('booking/email/confirm_reservation_email.html', 
                                        {'reservation': self,
                                         'check_in_weekday': self.check_in_date.strftime("%A"),
                                         'check_in_day': self.check_in_date.day,
                                         'check_in_month': self.check_in_date.strftime("%B"),
                                         'check_in_year': self.check_in_date.year,

                                         'check_out_weekday': self.check_out_date.strftime("%A"),
                                         'check_out_day': self.check_out_date.day,
                                         'check_out_month': self.check_out_date.strftime("%B"),
                                         'check_out_year': self.check_out_date.year,
                                        })
        subject = f"{self.guest.name} aquí tiene su confirmación de reserva en CoralBlanco"
        # Create an EmailMessage object.
        email = EmailMessage(
            subject,
            html_content,
            from_email= settings.DEFAULT_FROM_EMAIL,
            to = [self.guest.email],
        )
        # Set the content type to HTML
        email.content_subtype = 'html'
        # Send the email
        email.send()
        # Set this reservation as complete.
        self.completed = True
        self.save()

    @staticmethod
    def csv_file_name():
        return 'Reservations'
    
    @staticmethod
    def csv_headers():
        return ['Room', 'Adults', 'Children', 'Total Price', 'Check In', 'Check Out']
    
    @staticmethod
    def csv_attributes():
        return ['room', 'adults', 'children', 'total_price', 'check_in_date', 'check_out_date']
    
    def __str__(self):
        return f"Reservation of {self.user.username}\nNights: {self.nights}\nPrice: {self.reservation_price}\nTaxes: {self.taxes}\nTotal: {self.total_price}" 

# This table will relate to the user's reservation, it contains the guest info.
class Guest(models.Model):
    user_reservation = models.OneToOneField(
        Reservation,
        related_name='guest',
        on_delete=models.CASCADE,
        editable=False,
        null=True,
    )

    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    country = models.CharField(max_length=2, default='US')
    postal_code = models.CharField(max_length=20, null=True) 

    @staticmethod
    def csv_file_name():
        return 'Guests'
    
    @staticmethod
    def csv_headers():
        return ['Name', 'Last Name', 'Email', 'Country', 'Postal Code']
    
    @staticmethod
    def csv_attributes():
        return ['name', 'last_name', 'email', 'country', 'postal_code']
    
    def __str__(self):
        return f'{self.name} {self.last_name}'
    

"""Room Reservations refers to the tables that contain all the reservations that have been made to a room."""
class RoomReservations(models.Model):
    id = models.AutoField(primary_key=True)

    room = models.ForeignKey(
        Room, on_delete = models.CASCADE,
    ) # with this we can know the type, and price.
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        null=True
    )
    # Can acces the reservation with RoomReservations.reservation.
    check_in_date = models.DateField(null=True)
    check_out_date = models.DateField(null=True) # remember to add null false.
