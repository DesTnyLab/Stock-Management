from django.urls import path
from .views import manage_inventory

urlpatterns = [
    path('', manage_inventory, name='manage_inventory'),
]
