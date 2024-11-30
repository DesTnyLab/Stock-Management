from django.urls import path
from .views import *


urlpatterns = [
    path('', manage_inventory, name="manage_inventory"),
    path('<int:id>/', view_product_details, name= "product_history" ),
    # path('product-report/<int:id>/', sales_and_purchase_report, name="product_report"),

    path('search-stock/', product_stock_search_ajax, name='product_stock_search_ajax'),  # AJAX search view for stock
]

