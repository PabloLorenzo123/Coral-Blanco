from django.contrib import admin
from .models import RoomType, Room, Image, Reservation, RoomReservations, Guest

# Register your models here.
class ImageInline(admin.TabularInline):
    model = Image

class RoomTypeAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
    ]
    list_display = ('type', 'price',)

    
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Room)
admin.site.register(Image)
admin.site.register(Reservation)
admin.site.register(RoomReservations)
admin.site.register(Guest)