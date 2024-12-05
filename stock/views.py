from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from .models import *
from .forms import *
from datetime import date
from collections import defaultdict
from django.db.models import F, ExpressionWrapper, IntegerField
import matplotlib.pyplot as plt
import io
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from weasyprint import HTML
from django.template.loader import render_to_string
from datetime import datetime

from .forms import BillForm, BillItemProductFormSet
from .models import Bill, BillItem, BillItemProduct


def login(request):
    return render(request, "stock/login.html")


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
    stocks = Stock.objects.annotate(
        rem_stock=ExpressionWrapper(
            F("total_purchased") - F("total_sold"), output_field=IntegerField()
        )
    ).order_by("rem_stock")[
        :5
    ]  # Order by remaining_stock and limit to top 10

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
    stocks = Stock.objects.all()

    return render(
        request,
        "stock/stock.html",
        {
            "stocks": stocks,
        },
    )


def product_stock_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get("query", "")

    stocks = Stock.objects.filter(product__name__icontains=query)

    return render(
        request, "stock/product_stock_search_results.html", {"stocks": stocks}
    )


def view_product_details(request, id):
    # Get the product object
    product = get_object_or_404(Product, id=id)

    # Filter purchases based on the product name
    purchase_data = Purchase.objects.filter(product=product.name)

    sale_data = Sale.objects.filter(product=product)

    return render(
        request,
        "stock/product_details.html",
        context={
            "product": product,
            "purchase_data": purchase_data,
            "sale_data": sale_data,
        },
    )


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
    sale_data = Sale.objects.filter(date=today).select_related("product")
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
    sorted_sales = sorted(
        sales_summary.items(), key=lambda x: x[1]["revenue"], reverse=True
    )
    top_sales = sorted_sales[:5]
    total_revenue = sum(data["revenue"] for data in sales_summary.values())
    # Prepare data for the graph
    product_names = [item[0] for item in top_sales]
    quantities = [item[1]["quantity"] for item in top_sales]

    # Create a bar graph
    fig, ax = plt.subplots()
    ax.bar(product_names, quantities, color="skyblue")

    # Add labels to the bars
    for i, v in enumerate(quantities):
        ax.text(
            i, v + 0.1, str(v), ha="center", va="bottom"
        )  # Display quantity value above each bar

    # Add title and labels
    ax.set_title("Top 5 Sales Products for Today")
    ax.set_xlabel("Product Name")
    ax.set_ylabel("Quantity Sold")

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Convert the image to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Close the plot to release memory
    plt.close(fig)
    # print(img_str)
    # with open('test_image.png', 'wb') as f:
    #     f.write(buf.getvalue())

    return render(
        request,
        "stock/today_report.html",
        {
            "sales_summary": top_sales,
            "today": today,
            "graph": img_str,
            "total_profit": total_profit,
            "total_revenue": total_revenue,
        },
    )


def overall_top_sales(request):
    # Fetch all stock data
    stock_data = Stock.objects.select_related("product").all()
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
    sorted_sales = sorted(
        sales_summary.items(), key=lambda x: x[1]["revenue"], reverse=True
    )

    # Get the top 5 products
    top_sales = sorted_sales[:10]
    total_revenue = sum(data["revenue"] for data in sales_summary.values())
    # Prepare data for the graph
    product_names = [item[0] for item in top_sales]
    quantities = [item[1]["quantity"] for item in top_sales]

    # Create a bar graph
    fig, ax = plt.subplots()
    ax.bar(product_names, quantities, color="skyblue")

    # Add labels to the bars
    for i, v in enumerate(quantities):
        ax.text(
            i, v + 0.1, str(v), ha="center", va="bottom"
        )  # Display quantity value above each bar

    # Add title and labels
    ax.set_title("Top 5 Sales Products ")
    ax.set_xlabel("Product Name")
    ax.set_ylabel("Quantity Sold")

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Convert the image to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Close the plot to release memory
    plt.close(fig)

    return render(
        request,
        "stock/overall_report.html",
        {
            "sales_summary": top_sales,
            "graph": img_str,
            "total_profit": overall_profit,
            "total_revenue": total_revenue,
        },
    )



def create_bill(request):
    products = Product.objects.all()
    customers = Customer.objects.all()
    return render(request, 'create_bill.html', {'products': products, 'customers': customers})


@csrf_exempt
def add_bill_item_ajax(request):
    if request.method == 'POST':
        bill_id = request.POST.get('bill_id', None)
        bill_no = request.POST.get('bill_no')
        customer_id = request.POST.get('customer_id')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        rate = float(request.POST.get('rate', 0.0))

        # Ensure customer_id and product_id are provided
        if not customer_id or not product_id:
            return JsonResponse({'error': 'Customer and product must be provided.'}, status=400)

        # Create or get the bill
        if not bill_id:  # If bill_id is not provided, create a new bill
            bill = Bill.objects.create(
                bill_no=bill_no,
                customer_id=customer_id,
                date=now().date(),
            )
        else:  # Retrieve existing bill
            bill = get_object_or_404(Bill, id=bill_id, )

        # Create or get the BillItem for this bill
        bill_item, created = BillItem.objects.get_or_create(bill=bill)

        # Add a new BillItemProduct
        product = get_object_or_404(Product, id=product_id)
        bill_item_product = BillItemProduct.objects.create(
            bill_item=bill_item,
            product=product,
            quantity=quantity,
            rate=rate # Ensure rate is Decimal
        )

        # Update BillItem total
        bill_item.total += bill_item_product.get_subtotal() # Convert subtotal to Decimal
        bill_item.save()
     # Get or create a Credit instance for the given customer
        customer = get_object_or_404(Customer, id=customer_id)
        credit, created = Credit.objects.get_or_create(bill=bill, customer=customer)

        # Update the credit amount and date
        credit.amount = bill_item.total
        credit.date = now().date()
        credit.save()

        return JsonResponse({
            'bill_id': bill.id,
            'product_name': product.name,
            'quantity': bill_item_product.quantity,
            'rate': bill_item_product.rate,
            'subtotal': bill_item_product.get_subtotal(),
            'total': bill_item.total,
        })

    return JsonResponse({'error': 'Invalid method'}, status=400)



def generate_bill_pdf(request, bill_id):
    # Fetch the bill and related data
    bill = Bill.objects.get(id=bill_id)
    bill_items = bill.billitem_set.prefetch_related('products')

    # Context for the template
    context = {
        'bill': bill,
        'bill_items': bill_items,
        'total': sum(item.total for item in bill_items),
    }

    # Render the template to HTML
    html_string = render_to_string('bill_pdf_template.html', context)

    # Generate PDF from HTML
    pdf_file = HTML(string=html_string).write_pdf()

    # Create a response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bill_{bill.bill_no}.pdf"'

    return response


  


def generate_ledger(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    
    # Get all credit and debit transactions for the customer
    credits = Credit.objects.filter(customer=customer).order_by('date')
    debits = Debit.objects.filter(customer=customer).order_by('date')

    # Prepare a list of transactions to display
    transactions = []

    # Calculate the opening balance
    current_balance = 0.00
    # Merge credits and debits into a single list of transactions
    for credit in credits:
        transactions.append({
            'date': credit.date,
            'particulars': f"Bill No. {credit.bill.bill_no}" if credit.bill else "Credit",
            'debit': 0.00,
            'credit': credit.amount,
            'balance': None  # Will calculate later
        })

    for debit in debits:
        transactions.append({
            'date': debit.date,
            'particulars': "Cheque" if debit.amount > 0 else "Debit",
            'debit': debit.amount,
            'credit': 0.00,
            'balance': None  # Will calculate later
        })

    # Sort transactions by date
    transactions.sort(key=lambda x: x['date'])

    # Update the balance for each transaction
    for transaction in transactions:
        if transaction['credit'] > 0:
            current_balance += transaction['credit']
        if transaction['debit'] > 0:
            current_balance -= transaction['debit']
        transaction['balance'] = current_balance

    # Date range filtering
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = [txn for txn in transactions if start_date <= txn['date'] <= end_date]
        except ValueError:
            # Handle invalid date input
            pass
    debit_form = DebitForm()
    return render(request, 'ledger_page.html', {
        'customer': customer,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'debit_form':debit_form
    })



def debit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        debit_form = DebitForm(request.POST)
        if debit_form.is_valid():
            debit_instance = debit_form.save(commit=False)
            debit_instance.customer = customer
            debit_instance.save()
            
            # Update customer total_debit
            customer.total_debit += debit_instance.amount
            customer.save()

            messages.success(request, "Debit added successfully.")
            return redirect("generate_ledger", customer_id=customer.id)


   

