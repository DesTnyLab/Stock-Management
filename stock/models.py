from django.db import models

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


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name}"


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_purchased = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)

    @property
    def remaining_stock(self):
        return self.total_purchased - self.total_sold
