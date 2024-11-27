from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Stock
from .forms import PurchaseForm, SaleForm, ProductForm

def manage_inventory(request):


    #handel product form submisstion 
    if request.method == 'POST' and 'product_form' in request.POST:
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product_form.save()
            messages.success(request, "Product is added successfully.")
            return redirect('manage_inventory')
    else:
        product_form = ProductForm()

    # Handle purchase form submission
    if request.method == 'POST' and 'purchase_form' in request.POST:
        purchase_form = PurchaseForm(request.POST)
        if purchase_form.is_valid():
            purchase_form.save()
            messages.success(request, "Purchase added successfully.")
            return redirect('manage_inventory')
    else:
        purchase_form = PurchaseForm()

    # Handle sale form submission
    if request.method == 'POST' and 'sale_form' in request.POST:
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            sale_form.save()
            messages.success(request, "Sale added successfully.")
            return redirect('manage_inventory')
    else:
        sale_form = SaleForm()

    # Display stock
    stocks = Stock.objects.all()

    return render(request, 'manage_inventory.html', {
        'purchase_form': purchase_form,
        'product_form': product_form,
        'sale_form': sale_form,
        'stocks': stocks
    })
