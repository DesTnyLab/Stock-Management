from django.urls import path
from . import views

urlpatterns = [

    path('forecast/<int:product_id>/', views.product_forecast_view, name='product_forecast'),
]
