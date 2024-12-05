from django import forms
from .models import *
from django.forms import inlineformset_factory




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'quantity', 'price', 'date']
        widgets = {
        'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',  # Optional Bootstrap styling
        'placeholder': 'Select a date'
    }), }
        
    def clean_quantity(self):
            quantity = self.cleaned_data['quantity']
            product_name = self.cleaned_data['product']
            product, _ = Product.objects.get_or_create(name=product_name)
            stock, _ = Stock.objects.get_or_create(product=product)
          
            if stock.remaining_stock is None:
                raise forms.ValidationError("Stock data is invalid. Please check the stock record.")
            if quantity < 0:
                raise forms.ValidationError("Purchase quantity cannot be negative.")
            
            return quantity


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'price', 'date']
        widgets = {
        'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',  # Optional Bootstrap styling
        'placeholder': 'Select a date'
    }),}
        
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product = self.cleaned_data['product']
        stock = Stock.objects.get(product=product)
        if stock.total_purchased is None or stock.total_sold is None:
            raise forms.ValidationError("Stock data is invalid. Please check the stock record.")
        if quantity < 0:
            raise forms.ValidationError("Sale quantity cannot be negative.")
        if quantity > stock.total_purchased:
            raise forms.ValidationError(f"Cannot sell {quantity} units. Only {stock.total_purchased} units available.")
        return quantity



class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['bill_no', 'customer', 'date']

class BillItemProductForm(forms.ModelForm):
    class Meta:
        model = BillItemProduct
        fields = ['product', 'quantity', 'rate']

# Inline formset to handle multiple BillItemProducts for a single BillItem
BillItemProductFormSet = inlineformset_factory(
    BillItem, 
    BillItemProduct, 
    form=BillItemProductForm,
    extra=1,  # Number of empty forms to display
    can_delete=True  # Allow deletion of items
)



class DebitForm(forms.ModelForm):
    class Meta:
        model = Debit
        fields = ['amount', 'date']
        