from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Stock, Product, Purchase, Sale
from .forms import PurchaseForm, SaleForm, ProductForm
import json

def manage_inventory(request):

    # handel product form submisstion
    if request.method == "POST" and "product_form" in request.POST:
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product_form.save()
            messages.success(request, "Product is added successfully.")
            return redirect("manage_inventory")
    else:
        product_form = ProductForm()

    # Handle purchase form submission
    if request.method == "POST" and "purchase_form" in request.POST:
        purchase_form = PurchaseForm(request.POST)
        if purchase_form.is_valid():
            purchase_form.save()
            messages.success(request, "Purchase added successfully.")
            return redirect("manage_inventory")
    else:
        purchase_form = PurchaseForm()

    # Handle sale form submission
    if request.method == "POST" and "sale_form" in request.POST:
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            sale_form.save()
            messages.success(request, "Sale added successfully.")
            return redirect("manage_inventory")
    else:
        sale_form = SaleForm()

    # Display stock
    stocks = Stock.objects.all()

    return render(
        request,
        "manage_inventory.html",
        {
            "purchase_form": purchase_form,
            "product_form": product_form,
            "sale_form": sale_form,
            "stocks": stocks,
        },
    )




def product_stock_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get('query', '')  
    
 
    stocks = Stock.objects.filter(product__name__icontains=query)  
    
   
    return render(request, 'product_stock_search_results.html', {'stocks': stocks})



def view_product_details(request, id):
    # Get the product object
    product = get_object_or_404(Product, id=id)

    # Filter purchases based on the product name
    purchase_data = Purchase.objects.filter(product=product.name)

    sale_data = Sale.objects.filter(product=product)
   
    return render(request, "purches_history.html", context={
        'product': product,
        'purchase_data': purchase_data,
        'sale_data': sale_data
    })



def sales_and_purchase_report(request, id):
    product = Product.objects.get(id=id)
    
    # Fetch purchase data for the specific product
    purchase_data = Purchase.objects.filter(product=product.name)
    purchase_dates = [purchase.date.strftime('%Y-%m-%d') for purchase in purchase_data]  # Convert date to string
    purchase_quantities = [purchase.quantity for purchase in purchase_data]
    purchase_costs = [float(purchase.get_total_cost()) for purchase in purchase_data]  # Convert Decimal to float
    
    # Fetch sale data for the specific product
    sale_data = Sale.objects.filter(product=product)
    sale_dates = [sale.date.strftime('%Y-%m-%d') for sale in sale_data]  # Convert date to string
    sale_quantities = [sale.quantity for sale in sale_data]
    sale_revenues = [float(sale.get_total_cost()) for sale in sale_data]  # Convert Decimal to float

    # Pass the data to the template, ensure to convert the lists to JSON strings
    return render(request, 'sales_purchase_report.html', {
        'product': product,
        'purchase_dates': json.dumps(purchase_dates),
        'purchase_quantities': json.dumps(purchase_quantities),
        'purchase_costs': json.dumps(purchase_costs),
        'sale_dates': json.dumps(sale_dates),
        'sale_quantities': json.dumps(sale_quantities),
        'sale_revenues': json.dumps(sale_revenues),
    })