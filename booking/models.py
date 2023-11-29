from django.db import models
import uuid

# Create your models here.
class RoomType(models.Model):
    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True,
    )
    type = models.CharField(max_length=255)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField()
    max_adults = models.IntegerField(blank=True, null=True)
    max_kids = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.type


class Room(models.Model):
    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True
    )
    number = models.IntegerField()
    block = models.IntegerField()
    building = models.IntegerField()
    floor = models.IntegerField()
    avaibility = models.BooleanField()
    type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="room_type",
    )

    def __str__(self):
        return self.number
    
class Image(models.Model):
    uuid = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        unique = True
    )
    image = models.ImageField(upload_to='rooms/', blank=True)
    alt = models.CharField(max_length=255)
    room_type = models.ForeignKey(
        RoomType,
        related_name="images",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.alt
