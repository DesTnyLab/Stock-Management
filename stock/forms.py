from django import forms
from .models import *
from django.forms import inlineformset_factory




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "HS_code",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "HS_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }



class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["product", "quantity", "price", "date"]
        widgets = {
           "product": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-placeholder": "Search products...",  # Placeholder
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "value": now().date(),
                }
            ),
        }
    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        product= self.cleaned_data["product"]
  
        stock, _ = Stock.objects.get_or_create(product=product)

        if stock.remaining_stock is None:
            raise forms.ValidationError(
                "Stock data is invalid. Please check the stock record."
            )
        if quantity < 0:
            raise forms.ValidationError("Purchase quantity cannot be negative.")

        return quantity

   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].empty_label = "Select item to purchase"

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["product", "quantity", "price", "date"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",  # Optional for validation
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",  # Allows decimals
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "Select a date",
                    "value": now().date(),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].empty_label = "Select item to sell"

    def clean_quantity(self):
            try:   
                quantity = self.cleaned_data["quantity"]
                product = self.cleaned_data["product"]
                stock = Stock.objects.get(product=product)
            except:
                 raise forms.ValidationError("Product not avialable in Stock")
            if stock.remaining_stock is None or stock.total_sold is None:
                raise forms.ValidationError(
                    "Stock data is invalid. Please check the stock record."
                )
            if quantity < 0:
                raise forms.ValidationError("Sale quantity cannot be negative.")
            if quantity > stock.remaining_stock:
                raise forms.ValidationError(
                    f"Cannot sell {quantity} units. Only {stock.remaining_stock} units available."
                )
            return quantity
     
           
           


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ["bill_no", "customer", "date", "discount", 'payment_type']

    def clean_discount(self):
        try:   
            discount = self.cleaned_data["discount"]
            if int(discount) > 100:
                raise forms.ValidationError('Discont cannot be more then 100%')
            if int(discount) < 0 :
                raise forms.ValidationError('Discount cannot be in negative')
        except Exception as e:
            raise forms.ValidationError(e)
        return discount

class BillItemProductForm(forms.ModelForm):
    class Meta:
        model = BillItemProduct
        fields = ["product", "quantity", "rate"]


# Inline formset to handle multiple BillItemProducts for a single BillItem
BillItemProductFormSet = inlineformset_factory(
    BillItem,
    BillItemProduct,
    form=BillItemProductForm,
    extra=1,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of items
)


class DebitForm(forms.ModelForm):
    class Meta:
        model = Debit
        fields = ["amount", "date"]
        widgets = {
           
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "id": "date",
                "value": now().date(),
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount < 0:
            raise forms.ValidationError("Amount Cannot be in Negative")

        return amount


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = [
            "name",
            "phone_number",
            "company",
            'pan_no'
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        # Check if the phone number contains only digits and has the correct length
        if not phone_number.isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number (digits only)."
            )

        if len(phone_number) < 9:
            raise forms.ValidationError("Phone number must be at least 9 digits long.")

        return phone_number




class SuppliersForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = [
            "name",
            "phone_number",
            "address",
            "pan",  # Correct field name based on the model
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        # Check if the phone number contains only digits
        if not phone_number.isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number (digits only)."
            )

        # Check the length of the phone number
        if len(phone_number) < 9:
            raise forms.ValidationError("Phone number must be at least 9 digits long.")

        return phone_number




class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['suppliers', 'date', 'payment_type']
        widgets = {
            "suppliers": forms.Select(attrs={
                "class": "form-control",
                "id": "suppliers",
                "data-placeholder": "Search Suppliers..."
            }),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "id": "date",
                "value": now().date(),
            }),
        }


    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=False)
        
        # Check if `order_no` is not set
        if not instance.order_no:
            last_order = Order.objects.order_by('id').last()
            instance.order_no = (last_order.order_no + 1) if last_order else 1

        # Save the instance if commit is True
        if commit:
            instance.save()
        return instance
    

class OrderItemProductForm(forms.ModelForm):
    class Meta:
        model = OrderItemProduct
        fields = ['product', 'quantity', 'rate']




class DebitFormForSuppliers(forms.ModelForm):
    class Meta:
        model = Suppliers_debit
        fields = ["amount", "date"]
        widgets = {
           
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "id": "date",
                "value": now().date(),
            }),
        }



    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount < 0:
            raise forms.ValidationError("Amount Cannot be in Negative")

        return amount






class LawyerForm(forms.ModelForm):
    class Meta:
        model = Lawyer
        fields = ['name', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Lawyer Name',
            'phone_number': 'Phone Number',
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['lawyer', 'transaction_type', 'amount', 'description']
        widgets = {
            'lawyer': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'transaction_type': 'Transaction Type',
            'amount': 'Amount',
            'description': 'Description (Optional)',
        }












class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': now().date()}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'amount': 'Investment Amount',
            'date': 'Investment Date',
            'description': 'Description (Optional)',
        }


class OtherRevenueForm(forms.ModelForm):
    class Meta:
        model = OtherRevenue
        fields = ['source', 'amount', 'date', 'description']
        widgets = {
            'source': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': now().date()}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'source': 'Revenue Source',
            'amount': 'Revenue Amount',
            'date': 'Revenue Date',
            'description': 'Description (Optional)',
        }
