from django.urls import path
from .views import *


urlpatterns = [
    path('', manage_inventory, name="manage_inventory"),
    path('search-stock/', product_stock_search_ajax, name='product_stock_search_ajax'),  # AJAX search view for stock
]

