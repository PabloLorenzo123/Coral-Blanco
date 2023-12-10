from django.urls import path
from .views import UpdateUser, PrivateArea

urlpatterns = [
    path("area_privada/", PrivateArea.as_view(), name='user_dashboard'),
    path("update_info/<uuid:uuid>", UpdateUser.as_view(), name='update_user'),

]