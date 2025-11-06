from django.utils import timezone
from stock.models import Product, Order, OrderItem, OrderItemProduct, Suppliers_credit
def create_order(ai_order_data):
    """
    Creates a real order based on the AI-generated order.
    """
    # 1️⃣ Create Order
    order_no = Order.objects.count() + 1

    order = Order.objects.create(
        order_no=order_no,
        suppliers=ai_order_data.suppliers,
        date=timezone.now().date(),
        payment_type="CREDIT"
    )

    # 2️⃣ Create OrderItem (container for products)
    order_item = OrderItem.objects.create(order=order)
    order_total = 0

    # 3️⃣ Add products
    for item in ai_order_data.items.all():
        for product_row in item.products.all():
            product_obj = product_row.product
            quantity = product_row.quantity
            rate = product_row.rate

            product_entry = OrderItemProduct.objects.create(
                order_item=order_item,
                product=product_obj,
                quantity=quantity,
                rate=rate
            )

            order_total += product_entry.get_subtotal()

    # 4️⃣ Save totals
    order_item.total = order_total
    order_item.save()

    order.total_amount = order_total
    order.save()

       # 3️⃣ Create Suppliers_credit object
    if not hasattr(order, "suppliers_credit"):
        Suppliers_credit.objects.create(
            suppliers=ai_order_data.suppliers,
            order=order,
            amount=order.total_amount,
            date=timezone.now().date()
        )


    return order