from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
# Register your models here.

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "email",
        "username",
        "name",
        'last_name',
        'birthdate',
        'country',
        "phone_number",
        "is_superuser",
    )

# Styling admin 
admin.site.site_header = "Coral Blanco"
admin.site.site_title = "Administración Hotel Coral Blanco"
admin.site.index_title = "Administración Hotel Coral Blanco"

admin.site.register(CustomUser, CustomUserAdmin)