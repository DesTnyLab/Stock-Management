from django.db import models
from django.utils.timezone import now
from stock.models import Product, Suppliers


class SalesForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    forecast_date = models.DateField()
    predicted_quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_date']
    
    def __str__(self):
        if self.product:
            return f"Forecast for {self.product.name} on {self.forecast_date}: {self.predicted_quantity}"
        return f"Overall Forecast {self.forecast_date}: {self.predicted_quantity}"


class Order(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_no = models.PositiveIntegerField(unique=True)
    suppliers = models.ForeignKey(
        Suppliers,
        on_delete=models.CASCADE,
        related_name="ai_orders"  # ✅ FIX: Avoid clash with stock.Order
    )
    date = models.DateField(default=now)
    total_amount = models.FloatField(default=0.00)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'Order No: {self.order_no}'

    def save(self, *args, **kwargs):
        self.total_amount = round(self.total_amount, 2)
        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    total = models.FloatField(default=0.00)

    def __str__(self):
        return f'Order ID: {self.order.id}'

    def save(self, *args, **kwargs):
        self.total = round(self.total, 2)
        super(OrderItem, self).save(*args, **kwargs)


class OrderItemProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ai_order_products"  # ✅ FIX: Avoid clash with stock.OrderItemProduct
    )
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_subtotal(self):
        return round(int(self.quantity) * float(self.rate), 2)

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity}, Rate: {self.rate}) for {self.order_item.order}"
