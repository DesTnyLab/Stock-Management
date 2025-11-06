from django.shortcuts import render, get_object_or_404
from stock.models import Product, Purchase, ProductEmailStatus
from inventory_ai.models import Order, OrderItemProduct
from django.shortcuts import redirect
from .forecasting import forecast_sales_prophet
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from .utils import create_order

def product_forecast_ajax(request, product_id):
    forecast_list, plot_div = forecast_sales_prophet(product_id=product_id, periods=7)

    forecast_table = [
        {"ds": f[0].date(), "yhat": f[1], "yhat_lower": f[2], "yhat_upper": f[3]}
        for f in forecast_list
    ]

    product_name = get_object_or_404(Product, id=product_id).name

    # Render only the forecast fragment
    return render(request, "inventory_ai/forecast.html", {
        "plot_div": plot_div,
        "forecast_table": forecast_table,
        "product_name": product_name,
    })




def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Gather all products under the order
    order_products = OrderItemProduct.objects.filter(order_item__order=order)

    if request.method == "POST":
        total_amount = 0

        for item in order_products:
            qty = request.POST.get(f"qty_{item.id}")
            rate = request.POST.get(f"rate_{item.id}")

            if qty is not None:
                item.quantity = int(qty)

            if rate is not None:
                item.rate = float(rate)

            item.save()
            total_amount += item.get_subtotal()

        # Update totals on the order
        order.total_amount = total_amount
        order.status = "PROCESSING"  # Change status after editing
        order.save()

        return redirect("edit_order", order_id=order.id)

    return render(request, "inventory_ai/edit_order.html", {
        "order": order,
        "order_products": order_products
    })


def orders_list(request):
    orders = Order.objects.select_related("suppliers").order_by("-date", "-id")
    return render(request, "inventory_ai/orders_list.html", {"orders": orders})


def change_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)

    # Ensure status is valid
    allowed_status = ["PENDING", "PROCESSING", "COMPLETED", "CANCELLED"]
    if status not in allowed_status:
        messages.error(request, "Invalid status!")
        return redirect("orders_list")
    
    if status == "COMPLETED" and order.status != "COMPLETED":
        create_order(order)
        for item in order.items.all():  # iterate over OrderItem
            for product_item in item.products.all():  # iterate over OrderItemProduct
                # Create Purchase
                Purchase.objects.create(
                    product=product_item.product,
                    quantity=product_item.quantity,
                    price=float(product_item.rate),  # store as float
                    date=date.today()
                )

                email_status_qs = ProductEmailStatus.objects.filter(product=product_item.product)
                if email_status_qs.exists():
                  email_status_qs.update(status="PENDING")

    order.status = status
    order.save()
    messages.success(request, f"Order #{order.order_no} status updated to {status}")

    return redirect("orders_list")


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = order.items.first()  # Since there's one item container in your logic
    products = order_item.products.all()

    return render(request, "inventory_ai/order_detail.html", {
        "order": order,
        "products": products,
    })