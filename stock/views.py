from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Stock, Product, Purchase, Sale
from .forms import PurchaseForm, SaleForm, ProductForm


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