from django.db import models
import uuid
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from .account_helper import COUNTRIES
from django.core.validators import RegexValidator, MinLengthValidator

# For null values on birthdate.
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractUser):

    id = models.AutoField(primary_key=True)
    # adding a uuid to avoid compromising the page.
    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True
    )

    name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=30)
    birthdate = models.DateField(default=timezone.now)
    address = models.CharField(max_length=100, default="none")
    city = models.CharField(max_length=50, default="none")

    country = models.CharField(
        max_length=2,
        choices=COUNTRIES,
        default="US",
    )

    phone_number = models.CharField(
        validators=[
            RegexValidator(regex=r'^(\d{10}|\d{15})$'),
            MinLengthValidator(limit_value=10, message='Phone number must be at least 10 digits.'),
        ],
        max_length=15,
        null=True,
    )

    postcode = models.CharField(
        validators=[
            RegexValidator(regex=r'^\d+$'),
            MinLengthValidator(limit_value=4),
        ],
        max_length=10,
        null=True,
    )
