from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Stock, Product, Purchase, Sale
from .forms import PurchaseForm, SaleForm, ProductForm
import json
from datetime import date 
from collections import defaultdict
from django.db.models import F, ExpressionWrapper, IntegerField
import matplotlib.pyplot as plt
import io
import urllib
import base64


def index(request):
    return render(request, 'stock/login.html')


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
    # stocks = Stock.objects.all().order_by('remaining_stock')[:5]
    # Annotate the queryset to calculate remaining_stock
    stocks = (
        Stock.objects.annotate(
            rem_stock=ExpressionWrapper(
                F('total_purchased') - F('total_sold'),
                output_field=IntegerField()
            )
        )
        .order_by('rem_stock')[:5]  # Order by remaining_stock and limit to top 10
    )


    return render(
        request,
        "stock/index.html",
        {
            "purchase_form": purchase_form,
            "product_form": product_form,
            "sale_form": sale_form,
            "stocks": stocks,
        },
    )

def view_stock(request):
    stocks =  Stock.objects.all()
            


    return render(request,
        "stock/stock.html",
        {
           
            "stocks": stocks,
        },
    )



def product_stock_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get('query', '')  
    
 
    stocks = Stock.objects.filter(product__name__icontains=query)  
    
   
    return render(request, 'stock/product_stock_search_results.html', {'stocks': stocks})



def view_product_details(request, id):
    # Get the product object
    product = get_object_or_404(Product, id=id)

    # Filter purchases based on the product name
    purchase_data = Purchase.objects.filter(product=product.name)

    sale_data = Sale.objects.filter(product=product)
   
    return render(request, "stock/product_details.html", context={
        'product': product,
        'purchase_data': purchase_data,
        'sale_data': sale_data
    })



# def sales_and_purchase_report(request, id):
#     product = Product.objects.get(id=id)
    
#     # Fetch purchase data for the specific product
#     purchase_data = Purchase.objects.filter(product=product.name)
#     purchase_dates = [purchase.date.strftime('%Y-%m-%d') for purchase in purchase_data]  # Convert date to string
#     purchase_quantities = [purchase.quantity for purchase in purchase_data]
#     purchase_costs = [float(purchase.get_total_cost()) for purchase in purchase_data]  # Convert Decimal to float
    
#     # Fetch sale data for the specific product
#     sale_data = Sale.objects.filter(product=product)
#     sale_dates = [sale.date.strftime('%Y-%m-%d') for sale in sale_data]  # Convert date to string
#     sale_quantities = [sale.quantity for sale in sale_data]
#     sale_revenues = [float(sale.get_total_cost()) for sale in sale_data]  # Convert Decimal to float

#     # Pass the data to the template, ensure to convert the lists to JSON strings
#     return render(request, 'sales_purchase_report.html', {
#         'product': product,
#         'purchase_dates': json.dumps(purchase_dates),
#         'purchase_quantities': json.dumps(purchase_quantities),
#         'purchase_costs': json.dumps(purchase_costs),
#         'sale_dates': json.dumps(sale_dates),
#         'sale_quantities': json.dumps(sale_quantities),
#         'sale_revenues': json.dumps(sale_revenues),
#     })








def overall_profit(request):
    stock_data = Stock.objects.all()
    overall_profit = 0
    for item in stock_data:
        profit_data = item.total_selling_cost - item.total_buying_cost
        overall_profit += profit_data

    return render(request, "overall_profit.html", {"total_profit": overall_profit})



def todays_top_sales(request):
    # Get today's date
    today = date.today()
    
    # Fetch sale data for today
    sale_data = Sale.objects.filter(date=today).select_related('product')
    total_profit = 0
    for sale in sale_data:
        cost_price = sale.product.cost_price
        selling_price = sale.product.selling_price
        quantity = sale.quantity
        profit = (selling_price - cost_price) * quantity
        total_profit += profit
    # Create sales summary
    sales_summary = defaultdict(lambda: {"quantity": 0, "revenue": 0})

    for item in sale_data:
        sales_summary[item.product.name]["quantity"] += item.quantity
        sales_summary[item.product.name]["revenue"] += item.quantity * item.price
    
    # Sort products by revenue in descending order and select top 5
    sorted_sales = sorted(sales_summary.items(), key=lambda x: x[1]["revenue"], reverse=True)
    top_sales = sorted_sales[:5]
    total_revenue = sum(data["revenue"] for data in sales_summary.values())
    # Prepare data for the graph
    product_names = [item[0] for item in top_sales]
    quantities = [item[1]["quantity"] for item in top_sales]
    
    # Create a bar graph
    fig, ax = plt.subplots()
    ax.bar(product_names, quantities, color='skyblue')
    
    # Add labels to the bars
    for i, v in enumerate(quantities):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom')  # Display quantity value above each bar
    
    # Add title and labels
    ax.set_title('Top 5 Sales Products for Today')
    ax.set_xlabel('Product Name')
    ax.set_ylabel('Quantity Sold')
    
       # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert the image to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')


    # Close the plot to release memory
    plt.close(fig)
    # print(img_str)
    # with open('test_image.png', 'wb') as f:
    #     f.write(buf.getvalue())

    return render(request, "stock/today_report.html", {
        "sales_summary": top_sales,
        "today": today,
        "graph": img_str,
        "total_profit": total_profit,
        'total_revenue':total_revenue
    })


def overall_top_sales(request):
    # Fetch all stock data
    stock_data = Stock.objects.select_related('product').all()
    overall_profit = 0
    for item in stock_data:
        profit_data = item.total_selling_cost - item.total_buying_cost
        overall_profit += profit_data

    # Dictionary to aggregate sales data per product
    sales_summary = defaultdict(lambda: {"quantity": 0, "revenue": 0})

    for item in stock_data:
        sales_summary[item.product.name]["quantity"] += item.total_sold
        sales_summary[item.product.name]["revenue"] += item.total_selling_cost

    # Sort products by total revenue in descending order
    sorted_sales = sorted(sales_summary.items(), key=lambda x: x[1]["revenue"], reverse=True)

    # Get the top 5 products
    top_sales = sorted_sales[:10]
    total_revenue = sum(data["revenue"] for data in sales_summary.values())
      # Prepare data for the graph
    product_names = [item[0] for item in top_sales]
    quantities = [item[1]["quantity"] for item in top_sales]
    
    # Create a bar graph
    fig, ax = plt.subplots()
    ax.bar(product_names, quantities, color='skyblue')
    
    # Add labels to the bars
    for i, v in enumerate(quantities):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom')  # Display quantity value above each bar
    
    # Add title and labels
    ax.set_title('Top 5 Sales Products ')
    ax.set_xlabel('Product Name')
    ax.set_ylabel('Quantity Sold')
    
       # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert the image to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')


    # Close the plot to release memory
    plt.close(fig)

    return render(request, "stock/overall_report.html", {
        "sales_summary": top_sales,
        "graph": img_str,
        "total_profit": overall_profit,
        'total_revenue':total_revenue
    })
