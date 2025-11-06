from django.contrib import admin

# Register your models here.

from .models import SalesForecast, Order, OrderItem, OrderItemProduct

admin.site.register(SalesForecast)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderItemProduct)
