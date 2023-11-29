from django.urls import path
from .views import UpdateUser, Home

urlpatterns = [
    path("update_info/<uuid:uuid>", UpdateUser.as_view(), name='update_user'),
    path("home/", Home.as_view(), name='home')
]