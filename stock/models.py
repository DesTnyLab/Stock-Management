from django.db import models
from django.utils.timezone import now
# from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField( unique=True, max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    product_code = models.CharField(max_length=50, default=' ') 
    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.CharField(max_length=255, default=" ")
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def get_total_cost(self):
        return self.quantity*self.price
    def __str__(self):
        return f"Purchase of {self.quantity} {self.product}"

    # def clean(self):
    #     """Custom validation to ensure quantity is valid."""
    #     if self.quantity is None:
    #         raise ValidationError("Error occure please recheck quantity")
    #     if self.quantity <= 0:
    #         raise ValidationError("Quantity must be greater than zero.")

    def save(self, *args, **kwargs):
        product_obj, created = Product.objects.get_or_create(name=self.product, defaults={'cost_price': self.price})
        self.product = product_obj
        if not created:
            product_obj.cost_price = self.price
            product_obj.save()
        
        super().save(*args, **kwargs)
        # Update stock after saving the purchase
        # stock, _ = Stock.objects.get_or_create(product=self.product)
        # stock.total_purchased += self.quantity
        # stock.save()

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()


    def get_total_cost(self):
        return self.quantity*self.price
    
    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name}"

    def save(self, *args, **kwargs):
        if self.price > 0:
            self.product.selling_price = self.price
            self.product.save() 
        super().save(*args, **kwargs)

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_purchased = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)
    total_buying_cost = models.FloatField( default=0.00)
    total_selling_cost = models.FloatField(default=0.00)

    @property
    def remaining_stock(self):
        return self.total_purchased - self.total_sold





class Customer(models.Model):
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50, default=' ')
    total_debit = models.FloatField(default=0.00)


    

    def __str__(self):
        return f'{self.name}'
    
    

class Bill(models.Model):
    bill_no = models.PositiveIntegerField(unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'Bill No: {self.bill_no}'


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    total = models.FloatField(default=0.00)

    def __str__(self):
        return f'Bill ID: {self.bill.id}'


class BillItemProduct(models.Model):
    bill_item = models.ForeignKey(BillItem, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_subtotal(self):
        return self.quantity * self.rate

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity}, Rate: {self.rate}) for {self.bill_item.bill}"


class Credit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default=' ')  # Auto-filled field

    def save(self, *args, **kwargs):
        # Auto-update particulars with Bill number
        if not self.particulars:
            self.particulars = f"Bill No: {self.bill.bill_no}"
        super(Credit, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer} credited on {self.date}'


class Debit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default='Cheque')  # Auto-filled field

    def save(self, *args, **kwargs):
        # Auto-update particulars for Debit
        if not self.particulars:
            self.particulars = "Cheque"
        super(Debit, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer} Debited on {self.date}'
