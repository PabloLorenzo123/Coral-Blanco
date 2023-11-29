from django.contrib import admin
from .models import RoomType, Room, Image

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