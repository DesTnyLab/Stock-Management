from django.urls import path
from . import views

urlpatterns = [

    path('product_forecast_ajax/<int:product_id>/', views.product_forecast_ajax, name='product_forecast_ajax'),
]
