from django.db import models
# from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField( unique=True, max_length=255)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Purchase of {self.quantity} {self.product}"

    # def clean(self):
    #     """Custom validation to ensure quantity is valid."""
    #     if self.quantity is None:
    #         raise ValidationError("Error occure please recheck quantity")
    #     if self.quantity <= 0:
    #         raise ValidationError("Quantity must be greater than zero.")

    def save(self, *args, **kwargs):
        product_obj, created = Product.objects.get_or_create(name=self.product)
        # self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)

        # Update stock after saving the purchase
        # stock, _ = Stock.objects.get_or_create(product=self.product)
        # stock.total_purchased += self.quantity
        # stock.save()

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_purchased = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)

    @property
    def remaining_stock(self):
        return self.total_purchased - self.total_sold
