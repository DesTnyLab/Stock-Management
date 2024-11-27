from django import forms
from .models import Purchase, Sale, Product


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
    }),
}



class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'price', 'date']
        widgets = {
    'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',  # Optional Bootstrap styling
        'placeholder': 'Select a date'
    }),
}

