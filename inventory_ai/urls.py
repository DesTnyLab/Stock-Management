from django.urls import path
from . import views

urlpatterns = [

    path('product_forecast_ajax/<int:product_id>/', views.product_forecast_ajax, name='product_forecast_ajax'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    path("orders/", views.orders_list, name="orders_list"),
     path("orders/<int:order_id>/status/<str:status>/", views.change_order_status, name="change_order_status"),
     path("orders/<int:order_id>/", views.order_detail, name="order_detail"),


]
