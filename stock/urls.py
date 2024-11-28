from django.urls import path
from .views import manage_inventory, hello_world


urlpatterns = [
    path("", manage_inventory, name="manage_inventory"),
    path("hello", hello_world, name="hello_world"),
]
