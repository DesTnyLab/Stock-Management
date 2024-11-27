from django.db import models
from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Purchase of {self.quantity} {self.product.name}"
    
    def clean(self):
        """Custom validation to ensure stock doesn't go negative."""
        stock, _ = Stock.objects.get_or_create(product=self.product)
        
        if self.quantity < 0:
            raise ValidationError("Purchase quantity cannot be negative.")
        # Update stock after a purchase
        stock.total_purchased += self.quantity
        if stock.remaining_stock < 0:
            raise ValidationError(f"Cannot make a sale of {self.quantity} units. Insufficient stock.")
        stock.save()

    def save(self, *args, **kwargs):
        self.clean()  # Call clean to validate before saving
        super().save(*args, **kwargs)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name}"
    def clean(self):
        """Custom validation to ensure sales don't exceed purchases."""
        stock = Stock.objects.get(product=self.product)
        if self.quantity < 0:
            raise ValidationError("Sale quantity cannot be negative.")
        if self.quantity > stock.total_purchased:
            raise ValidationError(f"Cannot sell {self.quantity} units. Only {stock.total_purchased} units available.")
        # Update stock after a sale
        stock.total_sold += self.quantity
        stock.save()

    def save(self, *args, **kwargs):
        self.clean()  # Call clean to validate before saving
        super().save(*args, **kwargs)



class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_purchased = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)

    @property
    def remaining_stock(self):
        return self.total_purchased - self.total_sold
