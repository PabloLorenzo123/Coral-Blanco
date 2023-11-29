from django.urls import path
from .views import UpdateUser

urlpatterns = [
    path("update_info/<uuid:uuid>", UpdateUser.as_view(), name='update_info'),
]