from django.contrib import admin
from .models import RoomType, Room, Image, ReservationCart, RoomReservations, Guest, Feature

# Register your models here.
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class RoomFeatureinLine(admin.TabularInline):
    model = RoomFeature

class RoomTypeAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
        RoomFeatureinLine
    ]
    list_display = ('type', 'price',)

    
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Room)
admin.site.register(Image)
admin.site.register(ReservationCart)
admin.site.register(RoomReservations)
admin.site.register(Feature)
admin.site.register(Guest)
