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
from django.template.loader import render_to_string
from datetime import datetime
from django.urls import reverse
from django.db import transaction
from django.views.generic import View
from num2words import num2words
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
import csv
from django.apps import apps
from django.conf import settings
from weasyprint import HTML, CSS
import os
from django.templatetags.static import static


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.GET.get("next", "/")  # Get the 'next' parameter or default to '/'
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url)  # Redirect to the next URL or home page
        else:
        
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def manage_inventory(request):
    # Handle sale form submission
    try:

        if request.method == "POST" and "sale_form" in request.POST:
            sale_form = SaleForm(request.POST)
            if sale_form.is_valid():
                sale_form.save()
                messages.success(request, "Sale added successfully.")
                return redirect("manage_inventory")
            else:
                # Add form errors to messages
                for field, errors in sale_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            sale_form = SaleForm()


        stocks = Stock.objects.annotate(
            rem_stock=ExpressionWrapper(
                F("total_purchased") - F("total_sold"), output_field=IntegerField()
            )
        ).order_by("rem_stock")[
            :5
        ]  # Order by remaining_stock and limit to top 10

        # Generate the sales graph using the TodaysTopSalesView class
        sales_view = TodaysTopSalesView()  # Instantiate the class
        today = date.today()
        sale_data = Sale.objects.filter(date=today).select_related("product")  # Fetch sales for today
        graph = sales_view.get_graph(sale_data)  # Get the graph
        
    
        # Return render with the graph and stocks
        return render(
            request,
            "stock/index.html",
            {
                "sale_form": sale_form,
                "stocks": stocks,
                "graph": graph,  # Pass graph as base64 string
            },
        )
    except Exception as e:
        messages.error(request, 'Product not avialable in Stock')
        return render(
            request,
            "stock/index.html",
            {
                "sale_form": sale_form,
                "stocks": stocks,
                "graph": graph,  # Pass graph as base64 string
            },
        )

@login_required
def view_stock(request):
    try: 
        stocks = Stock.objects.all()

        return render(
            request,
            "stock/stock.html",
            {
                "stocks": stocks,
            },
        )

    except Exception as e :
        messages.error(request, 'Product not avialable in Stock')
        return redirect('manage_inventory')





def product_stock_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get("query", "")

    stocks = Stock.objects.filter(product__name__icontains=query)

    return render(
        request, "stock/product_stock_search_results.html", {"stocks": stocks}
    )

@login_required
def view_product_details(request, id):
    try: 
        product = get_object_or_404(Product, id=id)

        # Filter purchases based on the product name
        purchase_data = Purchase.objects.filter(product=product)

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
    except Exception as e :
         messages.error(request, 'Product details avialable in Stock')
         return redirect('manage_inventory')




class TodaysTopSalesView(View):
    template_name = "stock/today_report.html"

    def get_sales_data(self):
        """Fetch and process sales data."""
        today = date.today()
        sale_data = Sale.objects.filter(date=today).select_related("product")

        total_profit = 0
        sales_summary = defaultdict(lambda: {"quantity": 0, "revenue": 0})

        for sale in sale_data:
            cost_price = sale.product.cost_price
            selling_price = sale.product.selling_price
            quantity = sale.quantity
            profit = (selling_price - cost_price) * quantity
            total_profit += profit

            sales_summary[sale.product.name]["quantity"] += quantity
            sales_summary[sale.product.name]["revenue"] += quantity * sale.price

        # Sort products by revenue and get top 5
        sorted_sales = sorted(
            sales_summary.items(), key=lambda x: x[1]["revenue"], reverse=True
        )
        top_sales = sorted_sales[:5]
        total_revenue = sum(data["revenue"] for data in sales_summary.values())

        return {
            "top_sales": top_sales,
            "total_profit": total_profit,
            "total_revenue": total_revenue,
        }

    def generate_graph(self, top_sales):
        """Generate a bar graph for top sales."""
        product_names = [item[0] for item in top_sales]
        quantities = [item[1]["quantity"] for item in top_sales]

        fig, ax = plt.subplots()
        ax.bar(product_names, quantities, color="skyblue")

        for i, v in enumerate(quantities):
            ax.text(i, v + 0.1, str(v), ha="center", va="bottom")

        ax.set_title("Top 5 Sales Products for Today")
        ax.set_xlabel("Product Name")
        ax.set_ylabel("Quantity Sold")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def get(self, request, *args, **kwargs):
        sales_data = self.get_sales_data()
        graph = self.generate_graph(sales_data["top_sales"])

        return render(
            request,
            self.template_name,
            {
                "sales_summary": sales_data["top_sales"],
                "today": date.today(),
                "graph": graph,
                "total_profit": sales_data["total_profit"],
                "total_revenue": sales_data["total_revenue"],
            },
        )

    def get_graph(self, request):
        """Provide the graph as a separate endpoint for reuse."""
        sales_data = self.get_sales_data()
        graph = self.generate_graph(sales_data["top_sales"])
        return JsonResponse({"graph": graph})


@login_required

def overall_top_sales(request):
    try:


        actual_finance = ActualFinance.objects.get(id=1)

        # Fetch all sales data
        sell_data = Sale.objects.all()
        overall_profit = actual_finance.profit
        total_revenue = actual_finance.revenue
        total_investment = actual_finance.investment
       

        # Calculate overall revenue and profit
      

        # Overall Revenue and Profit Graph
        fig1, ax1 = plt.subplots()
        categories = ["Total Revenue", "Total Profit"]
        values = [total_revenue, overall_profit]
        ax1.bar(categories, values, color=["skyblue", "orange"])

        # Add labels
        for i, v in enumerate(values):
            ax1.text(i, v + 0.1, f"{v:.2f}", ha="center", va="bottom")

        ax1.set_title("Overall Revenue and Profit")
        ax1.set_ylabel("Amount ($)")

        # Save first graph to BytesIO
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        graph1_str = base64.b64encode(buf1.getvalue()).decode("utf-8")
        plt.close(fig1)

        # Calculate daily sales for the last 7 days
        today = timezone.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        daily_revenue = []
        daily_profit = []

        for day in last_7_days:
            # Define the start and end of the day
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            # Filter sales for the specific day
            daily_sales = Sale.objects.filter(date__range=(day_start, day_end))
            
            # Calculate daily revenue and profit
            day_revenue = sum(item.price * item.quantity for item in daily_sales)
            day_profit = sum(
                (item.price - item.product.cost_price) * item.quantity
                for item in daily_sales
            )
            daily_revenue.append(day_revenue)
            daily_profit.append(day_profit)

        # Create a graph for daily revenue and profit
        fig2, ax2 = plt.subplots()
        index = range(len(last_7_days))
        bar_width = 0.35

        ax2.bar(index, daily_revenue, bar_width, label="Revenue", color="skyblue")
        ax2.bar(
            [i + bar_width for i in index],
            daily_profit,
            bar_width,
            label="Profit",
            color="orange",
        )

        ax2.set_title("Revenue and Profit for Last 7 Days")
        ax2.set_xticks([i + bar_width / 2 for i in index])
        ax2.set_xticklabels([day.strftime("%Y-%m-%d") for day in last_7_days], rotation=45)
        ax2.set_ylabel("Amount ($)")
        ax2.legend()

        # Save second graph to BytesIO
        buf2 = io.BytesIO()
        plt.savefig(buf2, format="png")
        buf2.seek(0)
        graph2_str = base64.b64encode(buf2.getvalue()).decode("utf-8")
        plt.close(fig2)

        return render(
            request,
            "stock/overall_report.html",
            {
                "graph1": graph1_str,
                "graph2": graph2_str,
                "total_profit": overall_profit,
                "total_revenue": total_revenue,
                "total_investment":total_investment,
                "daily_sales": zip(last_7_days, daily_revenue, daily_profit),
            },
        )
    except Exception as e:
        messages.error(request, str(e))
        return redirect('manage_inventory')


@login_required
def create_bill(request):
    products = Product.objects.all()
    customers = Customer.objects.all()
    return render(request, 'stock/create_bill.html', {'products': products, 'customers': customers})


@csrf_exempt
def add_bill_item_ajax(request):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                # Extract data from the request
                bill_id = request.POST.get('bill_id')
                customer_id = request.POST.get('customer_id')
                product_id = request.POST.get('product_id')
                try:
                    quantity = int(request.POST.get('quantity', 1))
                    rate = float(request.POST.get('rate', 0.0))
                    discount = int(request.POST.get('discount', 0))
                except ValueError:
                    return JsonResponse({'error': 'Invalid quantity, rate, or discount provided.'}, status=400)

                payment_type = request.POST.get('payment_type')

                # Validate required fields
                if not (customer_id and product_id):
                    return JsonResponse({'error': 'Customer and product must be provided.'}, status=400)

                # Get the last Bill and determine the bill_no
                last_bill = Bill.objects.order_by('-id').first()
                bill_no = (last_bill.bill_no + 1) if last_bill else 1

                # Create or fetch the Bill
                if not bill_id:
                    bill = Bill.objects.create(
                        bill_no=bill_no,
                        customer_id=customer_id,
                        discount=discount,
                        date=now().date(),
                        payment_type=payment_type
                    )
                else:
                    bill = get_object_or_404(Bill, id=bill_id)

                # Fetch the product
                product = get_object_or_404(Product, id=product_id)

                # Create or fetch the BillItem for the given Bill
                bill_item, created = BillItem.objects.get_or_create(bill=bill)

                # Create a new BillItemProduct
                bill_item_product = BillItemProduct.objects.create(
                    bill_item=bill_item,
                    product=product,
                    quantity=quantity,
                    rate=rate
                )

                # Calculate subtotal and update total
                subtotal = quantity * rate
                bill_item.total += subtotal
                bill_item.save()

                # Prepare the response
                return JsonResponse({
                    'bill_id': bill.id,
                    'product_name': product.name,
                    'product_id': product.id,
                    'quantity': quantity,
                    'rate': rate,
                    'item_id': bill_item_product.id,
                    'subtotal': subtotal,
                    'total': bill_item.total,
                })
            except Exception as e:
                return JsonResponse({'error': 'An error occurred: {}'.format(str(e))}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
def clear_create_bill(request, billId):
  try: 
    bill = Bill.objects.get(id=billId)
    bill_item = BillItem.objects.get(bill=bill)

    total = bill_item.total
    discount = bill.discount
    total_amount = total - ((total*discount)/100)
    bill.total_amount = total_amount
    bill.save()


    return redirect('create_bill')
  except Exception as e:
        
        messages.error(request, e)
        return redirect('create_bill')



def convert_to_nepali_currency(amount):
    """Convert a numeric amount to words in Nepalese currency format."""
    rupees = int(amount)  # Get the whole number part as Rupees
    paisa = round((amount - rupees) * 100)  # Get the fractional part as Paise
    
    # Convert Rupees to words
    rupees_in_words = num2words(rupees, lang='en')
    
    # Convert Paise to words (if any)
    if paisa > 0:
        paisa_in_words = num2words(paisa, lang='en')
        return f"{rupees_in_words} Rupees and {paisa_in_words} Paise"
    else:
        return f"{rupees_in_words} Rupees"




def  generate_bill_pdf(request, bill_id):
    try:
       
        # Fetch the bill and related data
        bill = Bill.objects.get(id=bill_id)
        bill_items = bill.billitem_set.prefetch_related('products')
        total = sum(item.total for item in bill_items)
        discount = bill.discount
        total_amount = total - ((discount*total)/100)
        bill.total_amount = total_amount
        bill.save()
        total_in_words = convert_to_nepali_currency(total_amount)
    
        logo_path1 = os.path.join(settings.STATIC_ROOT, "images/esewa.jpeg")
        with open(logo_path1, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        esewa_url = f"data:image/png;base64,{base64_image}"

        logo_path2 = os.path.join(settings.STATIC_ROOT, "images/fonepay.jpeg")
        with open(logo_path2, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        bank_url = f"data:image/png;base64,{base64_image}"

        logo_path3 = os.path.join(settings.STATIC_ROOT, "images/whatsup.jpeg")
        with open(logo_path3, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        whatsapp_url = f"data:image/png;base64,{base64_image}"
        # Context for the template
     
        context = {
            'bill': bill,
            'bill_items': bill_items,
            'total': total,
            'total_amount': total_amount,
            'total_in_words':total_in_words,
            'discount': discount,
            'whatsapp_url': whatsapp_url,
            'esewa_url': esewa_url,
            'bank_url': bank_url,
        }

        # Render the template to HTML
        html_string = render_to_string('stock/bill_pdf_template.html', context)
       
        # Generate PDF from HTML
    
      

        # Generate PDF from HTML
# Generate PDF from HTML
        pdf_file = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
        ).write_pdf(stylesheets=[CSS(string='@page { size: A5; margin: 10mm; }'
                                     )])


        # Create a response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Bill_{bill.bill_no}.pdf"'
        
        return response
    
    except Exception as e:
       
        messages.error(request, e)
    
        return redirect('create_bill')

  

@login_required
def generate_ledger(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        
        # Get all credit and debit transactions for the customer
        credits = Credit.objects.filter(customer=customer).order_by('date')
        debits = Debit.objects.filter(customer=customer).order_by('date')
        cashes = BillOnCash.objects.filter(customer=customer).order_by('date')
        # Prepare a list of transactions to display
        transactions = []

        # Calculate the opening balance
        current_balance = 0.00

        
        # Merge cash, credits and debits into a single list of transactions

        for cash in cashes:
            transactions.append({
                'date': cash.date,
                'particulars': f"Bill No. {cash.bill.bill_no}" if cash.bill else "Cash",
                'debit': 0.00,
                'credit': 0.00,
                'cash': cash.amount,
                'balance': None,  # Will calculate later
                'bill_no': cash.bill.bill_no
            })

        for credit in credits:
            transactions.append({
                'date': credit.date,
                'particulars': f"Bill No. {credit.bill.bill_no}" if credit.bill else "Credit",
                'debit': 0.00,
                'cash': 0.00,
                'credit': credit.amount,
                'balance': None,  # Will calculate later
                'bill_no': credit.bill.bill_no
            })

        for debit in debits:
            transactions.append({
                ''
                'date': debit.date,
                'particulars': "Cheque" if debit.amount > 0 else "Debit",
                'debit': debit.amount,
                'credit': 0.00,
                'cash': 0.00,
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
        return render(request, 'stock/ledger_page.html', {
            'customer': customer,
            'transactions': transactions,
            'start_date': start_date,
            'end_date': end_date,
            'debit_form':debit_form,
        
        })
    except Exception as e:
        messages.error(request, {e})
        return render(request, 'stock/ledger_page.html', {
            'customer': customer,
            'transactions': transactions,
            'start_date': start_date,
            'end_date': end_date,
            'debit_form':debit_form,
        
        })


@login_required
def debit(request, customer_id):
    try: 
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
            else:
                # Add form errors to messages
                for field, errors in debit_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
                return redirect("generate_ledger", customer_id=customer.id)
    except Exception as e:
        messages.error(request, e)
        return redirect('generate_ledger', customer_id=customer.id)
   



@login_required
def customer_view_and_create(request):
    if request.method == 'POST':
        # Handle form submission
        customer_form = CustomerForm(request.POST)

        if customer_form.is_valid():
            customer_form.save()
            messages.success(request, "Customer added successfully.")
            return redirect('customer_details')
        else:
            # Add form errors to messages
            for field, errors in customer_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        # Handle GET request
        customer_form = CustomerForm()

    customers = sorted(Customer.objects.all(), 
                       key=lambda c: c.remaning_credit_to_pay, 
                       reverse=True)


    return render(request, 'stock/view_customers.html', {
        'customers': customers,
        'customer_form': customer_form,
    })

def view_customer_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get("query", "")

    customer = Customer.objects.filter(name__icontains=query)

    return render(
        request, "stock/view_customer_on_search.html", {"customers": customer}
    )





@login_required
def manage_product_and_purchase(request):

    try: 
        # handel product form submisstion
        if request.method == "POST" and "product_form" in request.POST:
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, "Product is added successfully.")
                return redirect("manage_product_and_purchase")
            else:
                # Add form errors to messages
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            product_form = ProductForm()


        # Handle purchase form submission
        if request.method == "POST" and "purchase_form" in request.POST:
            purchase_form = PurchaseForm(request.POST)

            if purchase_form.is_valid():
                purchase_form.save()
                messages.success(request, "Purchase added successfully.")
                return redirect("manage_product_and_purchase")
            else:
                # Add form errors to messages
                for field, errors in purchase_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            purchase_form = PurchaseForm()

        products =  Product.objects.all()

        return render(
            request,
            "stock/product.html",
            {
                "purchase_form": purchase_form,
                "product_form": product_form,
                "products": products,
            },
        )
    except Exception as e:
        messages.error(request, e)
        return redirect('manage_inventory')


@login_required
def view_product_search_ajax(request):
    """AJAX view to search product sock details."""
    query = request.GET.get("query", "")

    product = Product.objects.filter(name__icontains=query)

    return render(
        request, "stock/view_product_on_search.html", {"products": product}
    )




@login_required
def delete_bill_item(request, bill_id, item_id):
    if request.method == "POST":
        try:
            # Find and delete the bill ite
            bill_item = BillItem.objects.get(bill_id=bill_id)
            bill_item_product = BillItemProduct.objects.get(bill_item=bill_item, id=item_id)
            bill_item_product.delete()

            # Recalculate total
            
            remaining_items = BillItemProduct.objects.filter(bill_item=bill_item)
            total = sum(item.quantity * item.rate for item in remaining_items)
            bill_item.total = total
            bill_item.save()

            bill = Bill.objects.get(id=bill_id)
            amount = total -((total * bill.discount)/100)
            bill.total_amount = amount
            bill.save()

            return JsonResponse({'success': True, 'total': total})
        except BillItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bill item not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@login_required
def bill_details(request, bill_no):
    try: 
        bill = Bill.objects.get(bill_no=bill_no)
        bill_item = BillItem.objects.get(bill = bill)
        bill_item_product = BillItemProduct.objects.filter(bill_item=bill_item)
        context = {
            'responses' : bill_item_product,
            'customer': bill.customer,
            'bill_no': bill.bill_no,
            'total': bill_item.total,
            'discount': bill.discount,
            'total_amount': bill.total_amount

                }
        return render(request, 'stock/bill_details.html', context=context)
    except Exception as e:
        messages.error(request, e)
        return redirect('generate_ledger')


@login_required
def delete_product(request, id):
    try:
        # Use get_object_or_404 for cleaner error handling
        product = get_object_or_404(Product, id=id)
        product.delete()
        messages.success(request, "Product deleted successfully")
    except Exception as e:
        # Log the exception for debugging
       
        messages.error(request, "Failed to delete product")
    
    return redirect('manage_product_and_purchase')




def form_search_for_product(request):

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            term = request.GET.get('term')
            product = Product.objects.all().filter(name__icontains=term)
            return JsonResponse(list(product.values()), safe=False)


def form_search_for_customer(request):

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            term = request.GET.get('term')
            customer = Customer.objects.all().filter(name__icontains=term)
            return JsonResponse(list(customer.values()), safe=False)



def form_search_for_suppliers(request):

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            term = request.GET.get('term')
            suppliers = Suppliers.objects.all().filter(name__icontains=term)
            return JsonResponse(list(suppliers.values()), safe=False)






@login_required
def suppliers_view_and_create(request):
    try: 
        if request.method == 'POST':
            # Handle form submission
            suppliers_form = SuppliersForm(request.POST)

            if suppliers_form.is_valid():
                suppliers_form.save()
                messages.success(request, "Suppliers added successfully.")
                return redirect('suppliers_details')
            else:
                # Add form errors to messages
                for field, errors in suppliers_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            # Handle GET request
            suppliers_form = SuppliersForm()

        # Fetch all customers for listing
        suppliers = sorted(Suppliers.objects.all(), 
                           key=lambda c: c.remaning_credit_to_pay, 
                           reverse=True)

        return render(request, 'stock/view_suppliers.html', {
            'suppliers': suppliers,
            'suppliers_form': suppliers_form,
        })
    except Exception as e:
        messages.error(request, e)
        return redirect('manage_inventory')

def view_suppliers_search_ajax(request):
    """AJAX view to search product stock details."""
    query = request.GET.get("query", "")

    supplier = Suppliers.objects.filter(name__icontains=query)

    return render(
        request, "stock/view_suppliers_on_search.html", {"suppliers": supplier}
    )


@login_required
def create_order(request):
    if request.method == 'POST':
        if 'order_submit' in request.POST:  # Handle OrderForm submission
            form = OrderForm(request.POST)
            if form.is_valid():
                order = form.save()
                return JsonResponse({'success': True, 'order_id': order.id})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif 'product_submit' in request.POST:  # Handle ProductForm submission
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product = product_form.save()
                return JsonResponse({'success': True, 'product_id': product.id})
            return JsonResponse({'success': False, 'errors': product_form.errors})

    # Display both forms on GET
    form = OrderForm()
    product_form = ProductForm()
    products = Product.objects.all()

    return render(request, 'stock/create_order.html', {
        'form': form,
        'product_form': product_form,
        'products': products,
    })


@csrf_exempt
def add_order_product(request, order_id):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                data = json.loads(request.body)

                # Parse input data
                product_name = data.get('product_name')
                hs_code = data.get('hs_code', '')
                quantity = int(data.get('quantity', 1))
                rate = float(data.get('rate', 0.00))

                # Create or fetch the product
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        'HS_code': hs_code,
                        'cost_price': rate,
                        'selling_price': rate,
                    }
                )

            
                order = get_object_or_404(Order, id=order_id)

                # Get or create the OrderItem
                order_item, _ = OrderItem.objects.get_or_create(order=order)

                # Avoid duplicating products in the same order item
                order_product, order_product_created = OrderItemProduct.objects.get_or_create(
                    order_item=order_item,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'rate': rate,
                    }
                )

                if not order_product_created:
                    # If the product already exists, update its quantity and rate
                    order_product.quantity += quantity
                    order_product.rate = rate
                    order_product.save()



                subtotal = order_product.quantity * order_product.rate
                order_item.total += subtotal
                order_item.save()

                order.total_amount += subtotal
                order.save()

                # Add to Purchase if it doesn't already exist
                Purchase.objects.create(
                    product=product,
                
                        quantity= quantity,
                        price=rate,
                    date=now(),
                    
                )
            

                return JsonResponse({
                    'success': True,
                    'product': {
                        'name': product.name,
                        'hs_code': product.HS_code,
                        'quantity': order_product.quantity,
                        'rate': order_product.rate,
                        'subtotal': order_product.get_subtotal(),
                        'product_created': created,
                        'purchase_created': True,
                    }
                })
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})





@login_required
def generate_ledger_of_suppliers(request, suppliers_id):
    try:
        suppliers = Suppliers.objects.get(id=suppliers_id)
        
        # Get all credit and debit transactions for the customer
        credits = Suppliers_credit.objects.filter(suppliers=suppliers).order_by('date')
        debits = Suppliers_debit.objects.filter(suppliers=suppliers).order_by('date')
        cashes = OrderOnCash.objects.filter(suppliers=suppliers).order_by('date')
        # Prepare a list of transactions to display
        transactions = []

        # Calculate the opening balance
        current_balance = 0.00

        
        # Merge cash, credits and debits into a single list of transactions

        for cash in cashes:
            transactions.append({
                'date': cash.date,
                'particulars': f"Order No. {cash.order.order_no}" if cash.order else "Cash",
                'debit': 0.00,
                'credit': 0.00,
                'cash': cash.amount,
                'balance': None,  # Will calculate later
                'order_no': cash.order.order_no
            })

        for credit in credits:
            transactions.append({
                'date': credit.date,
                'particulars': f"Order No. {credit.order.order_no}" if credit.order else "Credit",
                'debit': 0.00,
                'cash': 0.00,
                'credit': credit.amount,
                'balance': None,  # Will calculate later
                'order_no': credit.order.order_no
            })

        for debit in debits:
            transactions.append({
                ''
                'date': debit.date,
                'particulars': "Cheque" if debit.amount > 0 else "Debit",
                'debit': debit.amount,
                'credit': 0.00,
                'cash': 0.00,
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
        return render(request, 'stock/suppliers_ledger_page.html', {
            'suppliers': suppliers,
            'transactions': transactions,
            'start_date': start_date,
            'end_date': end_date,
            'debit_form':debit_form,
        
        })
    except Exception as e:
        messages.error(request, {e})
        return render(request, 'stock/suppliers_ledger_page.html', {
            'suppliers': suppliers,
            'transactions': transactions,
            'start_date': start_date,
            'end_date': end_date,
            'debit_form':debit_form,
        
        })



@login_required
def suppliers_debit(request, suppliers_id):
  
    suppliers = get_object_or_404(Suppliers, id=suppliers_id)
    try:
        if request.method == "POST":
            debit_form = DebitFormForSuppliers(request.POST)
            if debit_form.is_valid():
                debit_instance = debit_form.save(commit=False)
                debit_instance.suppliers = suppliers
                debit_instance.save()
                
                # Update customer total_debit
                suppliers.total_debit += debit_instance.amount
                suppliers.save()

                messages.success(request, "Debit added successfully.")
                return redirect("generate_ledger_of_suppliers", suppliers_id=suppliers.id)
            else:
                # Add form errors to messages
                for field, errors in debit_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
                return redirect("generate_ledger_of_suppliers", suppliers_id=suppliers.id)
    except Exception as e:
        messages.error(request, e )
        return redirect("generate_ledger_of_suppliers", suppliers_id=suppliers.id)
    


@login_required
def clear_create_order(request, orderId):
  
    order = Order.objects.get(id=orderId)
    order_item = OrderItem.objects.get(order=order)

    total = order_item.total
    order.total_amount = total
    order.save()


    return redirect('create_bill')



@login_required
def delete_order_item(request, order_id, item_id):
    if request.method == "POST":
        try:
            
            order_item = OrderItem.objects.get(order_id=order_id)
            order_item_product = OrderItemProduct.objects.get(bill_item=order_item, id=item_id)
            order_item_product.delete()

            # Recalculate total
            
            remaining_items = OrderItemProduct.objects.filter(order_item=order_item)
            total = sum(item.quantity * item.rate for item in remaining_items)
            order_item.total = total
            order_item.save()

            order = Order.objects.get(id=order_id)
            order.total_amount = total
            order.save()

            return JsonResponse({'success': True, 'total': total})
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bill item not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)





@login_required
def order_details(request, order_no):
    try:
        order = Order.objects.get(order_no=order_no)
        order_item = OrderItem.objects.get(order = order)
        order_item_product = OrderItemProduct.objects.filter(order_item=order_item)
        context = {
            'responses' : order_item_product,
            'suppliers': order.suppliers,
            'order_no': order.order_no,
            'total': order.total_amount,

                }
        return render(request, 'stock/order_details.html', context=context)
    except Exception as e:
        messages.error(request, e)
        return redirect('manage_inventory')
     







@login_required
def edit_product(request, id):
    try:
        product = get_object_or_404(Product, id=id)

        if request.method == 'POST':
        
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
            
                return redirect('product_history', id=product.id)
        else:
        
            form = ProductForm(instance=product)

        return render(request, 'stock/edit_product.html', context={'form': form, 'product': product})
    except Exception as e:
        messages.error(request, e)
        return redirect('manage_inventory')
    


@login_required
def manage_lawyers(request):
    lawyers = Lawyer.objects.all()
    lawyer_form = LawyerForm()
    transaction_form = TransactionForm()

    if request.method == 'POST':
        if 'create_lawyer' in request.POST:
            lawyer_form = LawyerForm(request.POST)
            if lawyer_form.is_valid():
                lawyer_form.save()
                return redirect('manage_lawyers')
        elif 'add_transaction' in request.POST:
            transaction_form = TransactionForm(request.POST)
            if transaction_form.is_valid():
                transaction_form.save()
                return redirect('manage_lawyers')

    context = {
        'lawyers': lawyers,
        'lawyer_form': lawyer_form,
        'transaction_form': transaction_form,
    }
    return render(request, 'stock/manage_lawyers.html', context)





@login_required
def manage_finances(request):
    investments = Investment.objects.all()
    revenues = OtherRevenue.objects.all()

    investment_form = InvestmentForm()
    revenue_form = OtherRevenueForm()

    if request.method == 'POST':
        if 'add_investment' in request.POST:
            investment_form = InvestmentForm(request.POST)
            if investment_form.is_valid():
                investment_form.save()
                return redirect('manage_finances')

        elif 'add_revenue' in request.POST:
            revenue_form = OtherRevenueForm(request.POST)
            if revenue_form.is_valid():
                revenue_form.save()
                return redirect('manage_finances')

    context = {
        'investments': investments,
        'revenues': revenues,
        'investment_form': investment_form,
        'revenue_form': revenue_form,
    }
    return render(request, 'stock/manage_finances.html', context)







@login_required
def export_to_csv(request):
    # Specify your app name to filter models
    app_name = "stock"  # Replace with the name of your app

    # Create the HttpResponse object with appropriate headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="models_data.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Fetch models dynamically from the specified app
    models = [model for model in apps.get_models() if model._meta.app_label == app_name]

    for model in models:
        writer.writerow([f"Model: {model._meta.verbose_name}"])  # Write model name as a header
        fields = [field.name for field in model._meta.fields]
        writer.writerow(fields)  # Write field names

        # Write each object's data
        for obj in model.objects.all():
            row = [getattr(obj, field) for field in fields]
            writer.writerow(row)

        writer.writerow([])  # Blank line between models

    return response


















def custom_404_view(request, exception):
    return render(request, '404_error.html', status=404)

def custom_500_view(request):
    return render(request, '500_error.html', status=500)




