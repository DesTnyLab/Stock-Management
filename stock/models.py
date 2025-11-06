from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class Product(models.Model):
    name = models.CharField( unique=True, max_length=255)
    cost_price = models.FloatField(default=0.00)
    selling_price = models.FloatField(default=0.00)
    HS_code = models.CharField(max_length=50, default='')
    supplier_code = models.CharField(max_length=50, default='')
    
     
    def __str__(self):
        return f'{self.name}-{self.HS_code}'


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField(default=0.00)
    date = models.DateField()

    @property
    def get_total_cost(self):
        return self.quantity*self.price
    def __str__(self):
        return f"Purchase of {self.quantity} {self.product}"



    def save(self, *args, **kwargs):
        product_obj = Product.objects.get(id=self.product.id)
        
    
        product_obj.cost_price = self.price
        product_obj.save()
        
        super().save(*args, **kwargs)
     

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField(default=0.00)
    date = models.DateField()


    @property
    def get_total_cost(self):
        return self.quantity*self.price
    
    @property
    def profit(self):
        return (self.price - self.product.cost_price)*self.quantity

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name}"

    def save(self, *args, **kwargs):
        if self.price > 0:
            self.product.selling_price = self.price
            self.product.save() 
        super().save(*args, **kwargs)
    

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product = self.cleaned_data['product']
        stock = Stock.objects.get(product=product)
        if stock.remaining_stock is None or stock.total_sold is None:
            raise ValidationError("Stock data is invalid. Please check the stock record.")
        if quantity < 0:
            raise ValidationError("Sale quantity cannot be negative.")
        if quantity > stock.remaining_stock:
            raise ValidationError(f"Cannot sell {quantity} units. Only {stock.remaining_stock} units available.")
        return quantity
    
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
    phone_number = models.CharField(max_length=10, unique=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    pan_no = models.CharField(max_length=9, blank=True, null=True)

    def __str__(self):
        return f'{self.name} '

    @property
    def remaning_credit_to_pay(self):
        credits = Credit.objects.filter(customer=self)
        total_credit = sum([credit.amount for credit in credits])
        debits = Debit.objects.filter(customer=self)
        total_debit = sum([debit.amount for debit in debits])
        return total_credit - total_debit
    
class Bill(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash / QR'),
        ('CREDIT', 'Credit'),
    ]

    bill_no = models.PositiveIntegerField(unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()
    discount = models.IntegerField(default=0)
    total_amount = models.FloatField(default=0.00)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')

    def __str__(self):
        return f'Bill No: {self.bill_no}'

    def save(self, *args, **kwargs):
        # Save the bill
        self.total_amount = round(self.total_amount, 2)
        super(Bill, self).save(*args, **kwargs)




class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    total = models.FloatField(default=0.00)

    def __str__(self):
        return f'Bill ID: {self.bill.id}'
    def save(self, *args, **kwargs):
        # Auto-update particulars for Debit
        self.total = round(self.total, 2)
     
        super(BillItem, self).save(*args, **kwargs)

class BillItemProduct(models.Model):
    bill_item = models.ForeignKey(BillItem, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_subtotal(self):
        return round((self.quantity * self.rate),2)

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
        self.amount = round(self.amount, 2)
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
        self.amount = round(self.amount, 2)
        if not self.particulars:
            self.particulars = "Cheque"
        super(Debit, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer} Debited on {self.date}'




class BillOnCash(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default=' ')
    
    def save(self, *args, **kwargs):
        # Auto-update particulars with Bill number
        self.amount = round(self.amount, 2)
        if not self.particulars:
            self.particulars = f"Bill No: {self.bill.bill_no}"
        super(BillOnCash, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer} Cash on {self.date}'
    




class Suppliers(models.Model):
    name = models.CharField(max_length=255) 
    phone_number = models.CharField(max_length=10, unique=True)  
    pan = models.CharField(max_length=9, unique=True)
    total_debit = models.FloatField(default=0.00)
    address = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, default='')
    email = models.EmailField(max_length=255, blank=True, null=True, default="admin@admin.com")

    def __str__(self):
        return self.name

    @property
    def remaning_credit_to_pay(self):
        credits = Suppliers_credit.objects.filter(suppliers=self)
        total_credit = sum([credit.amount for credit in credits])
        debits = Suppliers_debit.objects.filter(suppliers=self)
        total_debit = sum([debit.amount for debit in debits])
        return total_credit - total_debit
   
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CREDIT', 'Credit'),
    ]

    
    order_no = models.PositiveIntegerField(unique=True)
    suppliers = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    date = models.DateField()
    total_amount = models.FloatField(default=0.00)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')


    def __str__(self):
        return f'Order No: {self.order_no}'

    def save(self, *args, **kwargs):
        # Save the bill
        self.total_amount = round(self.total_amount, 2)
        super(Order, self).save(*args, **kwargs)




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total = models.FloatField(default=0.00)

    def __str__(self):
        return f'Order ID: {self.order.id}'
    def save(self, *args, **kwargs):
        # Auto-update particulars for Debit
        self.total = round(self.total, 2)
     
        super(OrderItem, self).save(*args, **kwargs)

class OrderItemProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_subtotal(self):
        quantity = int(self.quantity)  # Ensure quantity is an integer
        rate = float(self.rate)  # Convert rate to a float
        return round(quantity * rate, 2)

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity}, Rate: {self.rate}) for {self.order_item.order}"


class ProductEmailStatus(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="email_statuses")
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    last_sent = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.product.name} - {self.supplier.name} - {self.status}"

class OrderOnCash(models.Model):
    suppliers = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default=' ')
    
    def save(self, *args, **kwargs):
        # Auto-update particulars with Bill number
        self.amount = round(self.amount, 2)
        if not self.particulars:
            self.particulars = f"Order No: {self.order.order_no}"
        super(OrderOnCash, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.suppliers} Cash on {self.date}'
    




class Suppliers_credit(models.Model):
    suppliers = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default=' ')  # Auto-filled field

    def save(self, *args, **kwargs):
        # Auto-update particulars with Bill number
        self.amount = round(self.amount, 2)
        if not self.particulars:
            self.particulars = f"Order no: {self.order.order_no}"
        super(Suppliers_credit, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.suppliers} credited on {self.date}'


class Suppliers_debit(models.Model):
    suppliers = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    date = models.DateField(default=now)
    particulars = models.CharField(max_length=255, editable=False, default='Cheque')  # Auto-filled field

    def save(self, *args, **kwargs):
        # Auto-update particulars for Debit
        self.amount = round(self.amount, 2)
        if not self.particulars:
            self.particulars = "Cheque"
        super(Suppliers_debit, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.suppliers} Debited on {self.date}'





            


class Lawyer(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be a valid 10-digit number."
            )
        ],
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DEBIT', 'Debit'),   # Lawyer takes money from you
        ('CREDIT', 'Credit'), # Lawyer gives money to you
    ]

    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(
        max_length=6, choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField(blank=True, null=True)  # Optional field for notes

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} by {self.lawyer.name}"







class Investment(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Investment of {self.amount} on {self.date}"


class OtherRevenue(models.Model):
    REVENUE_SOURCE_CHOICES = [
        ('PRINT', 'Printing '),
        ('FORM', 'Online Form'),
        ('OTHERS', 'Other Sources'),
    ]

    source = models.CharField(
        max_length=20, choices=REVENUE_SOURCE_CHOICES, default='OTHERS'
    )
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source} Revenue of {self.amount} on {self.date}"



class ActualFinance(models.Model):
    investment = models.FloatField(default=0)
    revenue = models.FloatField(default=0)
    profit = models.FloatField(default=0)



