from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Stock)
admin.site.register(Sale)

admin.site.register(Customer)
admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(BillItemProduct)


admin.site.register(Credit)
admin.site.register(Debit)
admin.site.register(BillOnCash)