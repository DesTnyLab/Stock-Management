from django import forms
from .models import Purchase, Sale, Product, Stock


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
            product = self.cleaned_data['product']
            stock, _ = Stock.objects.get_or_create(product=product)
            if stock.remaining_stock is None:
                raise forms.ValidationError("Stock data is invalid. Please check the stock record.")
            if quantity < 0:
                raise forms.ValidationError("Purchase quantity cannot be negative.")
            if stock.remaining_stock < quantity:
                raise forms.ValidationError(f"Not enough stock. Only {stock.remaining_stock} units available.")
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

