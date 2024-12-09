from django.urls import path
from .views import *


urlpatterns = [
    path("", manage_inventory, name="manage_inventory"),
    path("view-stock", view_stock, name="view_stock"),
    path('bills/create/', create_bill, name='create_bill'),
    path('bills/add-item/', add_bill_item_ajax, name='add_bill_item_ajax'),
    path('bills/pdf/<int:bill_id>/', generate_bill_pdf, name='generate_bill_pdf'),

    path("<int:id>/", view_product_details, name="product_history"),

    # path("today_top_sales", todays_top_sales, name="todays_top_sales"),
    path('sales-graph/', TodaysTopSalesView.as_view(), name='sales_graph'),
    path('sales-graph/json/', TodaysTopSalesView().get_graph, name='sales_graph_json'),  # for the graph in JSON format
    path("overall_top_sales", overall_top_sales, name="overall_top_sales"),
    path(
        "search-stock/", product_stock_search_ajax, name="product_stock_search_ajax"
    ),  

    path('customer/<int:customer_id>/transactions/', generate_ledger, name='generate_ledger'),
    path('debit/<int:customer_id>/', debit, name="debit"),
    path('customer-details', customer_view_and_create, name= 'customer_details'),

     path(
        "search-customer/", view_customer_search_ajax, name="view_customer_search_ajax"
    ),  
   path('products', manage_product_and_purchase, name='manage_product_and_purchase'),
    path(
        "search-product/", view_product_search_ajax, name="view_product_search_ajax"
    ),  

    path('bills/clear/<int:billId>/', clear_create_bill, name='clear'),

    path('bills/delete-item/<int:bill_id>/<int:item_id>/', delete_bill_item, name='delete_bill_item'),
    path('bill_details/<int:bill_no>/', test, name ='bill_details')
]
