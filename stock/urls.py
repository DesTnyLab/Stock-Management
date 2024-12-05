from django.urls import path
from .views import *


urlpatterns = [
    path("", manage_inventory, name="manage_inventory"),
    path("view-stock", view_stock, name="view_stock"),
    path("login", login, name="login"),
    path('bills/create/', create_bill, name='create_bill'),
    path('bills/add-item/', add_bill_item_ajax, name='add_bill_item_ajax'),
    path('bills/pdf/<int:bill_id>/', generate_bill_pdf, name='generate_bill_pdf'),

    path("<int:id>/", view_product_details, name="product_history"),
    # path('product-report/<int:id>/', sales_and_purchase_report, name="product_report"),
    path("today_top_sales", todays_top_sales, name="todays_top_sales"),
    path("overall_top_sales", overall_top_sales, name="overall_top_sales"),
    path(
        "search-stock/", product_stock_search_ajax, name="product_stock_search_ajax"
    ),  # AJAX search view for stock
]
