from django.contrib import admin
from .models import Product, Purchase, Sale, Stock

# Register your models here.

admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Stock)
admin.site.register(Sale)

