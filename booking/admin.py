from django.contrib import admin
from .models import RoomType, Room, Image, Reservation, RoomReservations, Guest, Feature, RoomFeature

# Register your models here.
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class GuestInline(admin.TabularInline):
    model = Guest
    extra = 1

class RoomFeatureinLine(admin.TabularInline):
    model = RoomFeature

class RoomTypeAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
        RoomFeatureinLine
    ]
    list_display = ('type', 'price',)

class ReservationAdmin(admin.ModelAdmin):
    inlines = [
        GuestInline
    ]

admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Room)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Guest)
admin.site.register(RoomFeature)
